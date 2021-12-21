$(document).ready(function(){

    var pageNum = 1
    var contentType = window.location.pathname.split('/')[1]
    var accountUsername = window.location.pathname.split('/')[2]

    var templateScript = document.querySelector('#post-template')
    if (templateScript){
        var postTemplate = Handlebars.compile(templateScript.innerHTML) 
    }

    $('#loadMore').click(LoadMorePosts)

    $('main').scroll(function(e){
        if ($('#loadMore').offset().top < 1200){
          console.log('hi')
        }
    });

    function LoadMorePosts(){
        var $loadButton =  $('#loadMore')
        console.log(contentType)
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
                data.posts.forEach(function(postData, i) {
                    var post = postTemplate(postData)
                    $('#loadMore').before(post)
                });
            } 
        })
    };






    //Like Post AJAX
    $(".post-like").click(function(){
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
    $(".post-stats").hover(function(e){
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