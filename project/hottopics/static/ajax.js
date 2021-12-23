$(document).ready(function(){
   
    var pageNum = 1
    var readyToLoad = true

    var contentType = window.location.pathname.split('/')[1]
    var accountUsername = window.location.pathname.split('/')[2]

    var templateScript = document.querySelector('#post-template')
    if (templateScript){
        var postTemplate = Handlebars.compile(templateScript.innerHTML) 
    }

    LoadMorePosts()
    

    $('main').scroll(function(e){
        if ($('#loadMore').offset().top < 1200 && readyToLoad){
            pageNum++
            readyToLoad = false
            LoadMorePosts()
        }
    });

    function LoadMorePosts(){
        $.ajax({
            url: '/api/loadMorePosts',
            type: "POST",
            DataType: "json",
            data: {
                'contentType': contentType,
                'accountUsername': accountUsername,
                'pageNum': pageNum,
            },

            success: function(data){
                if (data.error){
                    if (data.error == 'invalidContentType'){return}
                    if (data.error == 'noposts'){
                        if (contentType == 'home'){
                            response = 'Oops, something went wrong!'
                        } else if (contentType == 'following'){
                            response = "None of the accounts you follow have any posts"
                        } else if (contentType == 'favourites'){
                            response = "You don't have any favourites, go like some posts!"
                        } else if (contentType == 'account'){
                            if (data.ownAccount){
                                response = 'Create your own post for it to show here!'
                            }else{
                                response = 'This account has no posts'
                            }
                        }
                    } else if (data.error == 'notfollowing'){
                        response = "You're not following any accounts"
                    }
                    $(".post-response").text(response)
                    return
                }
    
                data.posts.forEach(function(postData, i) {
                    var post = postTemplate(postData)
                    $('#loadMore').before(post)
                    
                    choice = postData.choice
                    if (choice){
                        post = document.getElementById(postData.id)
                        choice_buttons = $(post).children('.post-choices').children() 
                        percentages = postData.percentages
                    
                        for (let i = 0; i < choice_buttons.length; i++){
                            if (choice==i+1){
                                var $text = $(choice_buttons[i]).children('.choice-text')[0]
                                var $span = $('<span>').addClass('voted-icon')
                                var $i = $('<i>').addClass('checkmark material-icons').html('done')
                                $span.append($i)
                                $text.after($i[0])
                            }
                            $(choice_buttons[i]).children('.choice-percentage').text(percentages[i]+'%').show()
                            $(choice_buttons[i]).children('.choice-percentage-bar').css('width', percentages[i]+'%')
                        }
                    }
                });

                readyToLoad = data.lastPage? false : true;
            } 
        })
    };


    //Vote AJAX
    $("main").on('click', '.post-choice', function(e){
        var choice = $(this).val()
        var post_id = $(this).parents('.post-container').attr('id')
        $.ajax({
            url: '/api/vote',
            type: "PUT",
            DataType: "json",
            data: {'post_id': post_id, "choice": choice},

            success: function(response){
                if (response.action=='alreadyvoted'){
                    return
                } else if (response.action=='voted'){
                    var choice_buttons = $(e.target).parent().children() 
                    percentages = response.percentages
                    for (let i = 0; i < choice_buttons.length; i++){
                        if (choice==i+1){
                            var $text = $(choice_buttons[i]).children('.choice-text')[0]
                            var $span = $('<span>').addClass('voted-icon')
                            var $i = $('<i>').addClass('checkmark material-icons').html('done')
                            $span.append($i)
                            $text.after($i[0])
                        }
                        $(choice_buttons[i]).children('.choice-percentage').text(percentages[i]+'%').fadeIn(100, 'linear')
                        $(choice_buttons[i]).children('.choice-percentage-bar').css('width', percentages[i]+'%').css('transition', 'width '+percentages[i]/100+'s ease-out')
                    }
                }   
            }
        }); 
    });


    //Like Post AJAX
    $("main").on('click', ".post-like", function(){
        var like_count = $(this).find('h5')
        var icon = $(this).find('i')
        var id = $(this).parents('.post-container').attr('id')
        $.ajax({
            url: '/api/like',
            type: "PUT",
            DataType: "json",
            data: {'post_id': id},

            success: function(response){
                if (response.action==='error') {return} 

                likes = parseInt(like_count.html())
                if (response.action === 'liked'){
                    icon.html('favorite')
                    if (typeof(likes) == 'number') {like_count.html(likes + 1)}
                } else if (response.action === 'unliked'){
                    icon.html('favorite_border')
                    if (typeof(likes) === 'number') {like_count.html(likes - 1)}
                }
            }
        });
    });

    //Follow/Unfollow AJAX
    $('#unfollowButton').click(FollowAPI)

    $('#follow-unfollow').click(function(e){
        var $followButton = $('#follow-unfollow')

        if ($followButton.hasClass('follow')){
            FollowAPI(e)
        } else if ($followButton.hasClass('following')){
            $('#unfollowModal').modal('show')
        }
    });

    $('#follow-unfollow').mouseenter(function(){
        var $followButton = $('#follow-unfollow')
        if ($followButton.hasClass('following')){
            $followButton.html("Unfollow?")
            $followButton.removeClass("account-following")
            $followButton.addClass("account-unfollow") 
        }
    });

    $('#follow-unfollow').mouseleave(function(){
        var $followButton = $('#follow-unfollow')
        if ($followButton.hasClass('following')){
            $followButton.html("Following")
            $followButton.addClass("account-following")
            $followButton.removeClass("account-unfollow")  
        }
    });

    function FollowAPI(e){
        var $followButton = $('#follow-unfollow')
        var follow_id = e.target.value
        $.ajax({
            url: '/api/follow',
            type: "PUT",
            DataType: "json",
            data: {'user_id': follow_id},

            success: function(response){
                if (response.action==='error') {return} 
              
                if ($followButton.html().trim() === "Follow"){
                    $followButton.html("Following")
                } else {
                    $followButton.html("Follow")
                }

                $followButton.toggleClass('account-following')
                $followButton.toggleClass('account-button')
                $followButton.toggleClass('following')
                $followButton.toggleClass('follow')  

            }
        });
    }


    //Like and Comment Hover CSS
    $("main").on("mouseenter mouseleave", ".post-stats", function(e){
        var $stat = $(e.currentTarget)
        var $icon = $stat.find('.post-icon')
        if ($stat.hasClass('post-comment')){
            $stat.toggleClass('comment-hover')
            $icon.toggleClass('icon-comment-hover')
        } else if ($stat.hasClass('post-like')){
            $stat.toggleClass('like-hover')
            $icon.toggleClass('icon-like-hover')
        }
    });

});