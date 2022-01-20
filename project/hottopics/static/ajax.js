$(document).ready(function(){
   
    var pageNum = 1
    var readyToLoad = true

    var contentType = window.location.pathname.split('/')[1]
    var accountUsername = window.location.pathname.split('/')[2]

    var templateScript = document.querySelector('#post-template')
    if (templateScript){
        var postTemplate = Handlebars.compile(templateScript.innerHTML) 
    }

    var commentScript = document.querySelector('#comment-template')
    if (commentScript){
        var commentTemplate = Handlebars.compile(commentScript.innerHTML) 
    }

    LoadMorePosts()
    LoadSideBarContent()


    $('main').scroll(function(e){
        if($('#loadMore')[0]){
            if ($('#loadMore').offset().top < 1200 && readyToLoad){
                pageNum++
                readyToLoad = false
                LoadMorePosts()
            }
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
                                response = 'This user has no posts'
                            }
                        }
                    } else if (data.error == 'notfollowing'){
                        response = "You're not following any accounts"
                    }
                    $(".post-response").text(response).show()
                    return
                }
                if (data.posts){
                    data.posts.forEach(function(postData, i) {
                        var post = postTemplate(postData)
                        $('#loadMore').before(post)
                        
                        choice = postData.choice
                        post = document.getElementById(postData.id)
                        if (choice){
                            choice_buttons = $(post).children('.post-choices').children() 
                            percentages = postData.percentages
                        
                            for (let i = 0; i < choice_buttons.length; i++){
                                if (choice==i+1){
                                    var $text = $(choice_buttons[i]).children('.choice-text')[0]
                                    var $i = $('<i>').addClass('checkmark material-icons').html('done')
                                    $text.after($i[0])
                                }
                                $(choice_buttons[i]).children('.choice-percentage').text(percentages[i]+'%').show()
                                $(choice_buttons[i]).children('.choice-percentage-bar').css('width', percentages[i]+'%')
                            }
                        }
                        if (data.ownAccount && contentType=='account'){
                            var $deletePost = $('<i>').addClass('deletePost material-icons').html('delete')
                            $(post).append($deletePost)
                        }
                    });
                }
                if (data.post){
                    var post = postTemplate(data.post)
                    $('.postComment').before(post).show()
                    $('#CommentInput')[0].placeholder = "Comment on " + data.post.author_username + "'s post"

                    
                    choice = data.post.choice
                    post = document.getElementById(data.post.id)
                    if (choice){
                        choice_buttons = $(post).children('.post-choices').children() 
                        percentages = data.post.percentages
                    
                        for (let i = 0; i < choice_buttons.length; i++){
                            if (choice==i+1){
                                var $text = $(choice_buttons[i]).children('.choice-text')[0]
                                var $i = $('<i>').addClass('checkmark material-icons').html('done')
                                $text.after($i[0])
                            }
                            $(choice_buttons[i]).children('.choice-percentage').text(percentages[i]+'%').show()
                            $(choice_buttons[i]).children('.choice-percentage-bar').css('width', percentages[i]+'%')
                        }
                    } 
                }
                if (data.comments){
                    data.comments.forEach(function(commentData, i){
                        var comment = commentTemplate(commentData)
                        $('#commentSection').append(comment)

                    });
                }

                readyToLoad = data.lastPage? false : true;
            } 
        })
    };

    function LoadSideBarContent(){
        $.ajax({
            url: '/api/loadSidebar',
            type: "GET",
            DataType: "json",

            success: function(data){
                var recommendedScript = document.querySelector('#recommended-template')
                if (recommendedScript){
                    var recommendedTemplate = Handlebars.compile(recommendedScript.innerHTML) 
                }

                data.recommended.forEach(function(userData, i){
                    if (userData.username.length > 14){
                        userData.username = userData.username.substring(0, 13) + '...' 
                    }
                    if (!(window.location.pathname.split('/')[1] == 'account' && window.location.pathname.split('/')[2] == userData.username)){
                        recommended = recommendedTemplate(userData)
                        $('.recommendedUsers').append(recommended)
                    }
                })            
                $('.recommendedContainer').show()
            }
        })
    }



    //Redirect to Post Route
    $('main').on('click', '.commentButtonLink', function(e){
        post_id = $(this).parents('.post-container').attr('id')
        console.log(post_id)
        window.location.href = '/post/'+ post_id
    });

    //Vote AJAX
    $("main").on('click', '.post-choice', function(e){
        var choice = $(this).val()
        var postContainer = $(this).parents('.post-container') 
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
                    
                    var choice_buttons = $(e.target).closest('.post-choices').children() 
                    percentages = response.percentages
                    if (response.alreadyVoted){
                        $($(choice_buttons[response.lastVote-1]).children('.checkmark')[0]).remove()
                    }else{
                        var vote_count = postContainer.find('#totalVoteCount')
                        votes = Number(vote_count.html())
                        if (votes || votes==0) {vote_count.html(votes + 1)} 
                    }
                    for (let i = 0; i < choice_buttons.length; i++){
                        if (choice==i+1){
                            var $text = $(choice_buttons[i]).children('.choice-text')[0]
                            var $i = $('<i>').addClass('checkmark material-icons').html('done')
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

                likes = Number(like_count.html())
                if (response.action === 'liked'){
                    icon.html('favorite')
                    if (likes || likes==0) {like_count.html(likes + 1)}
                } else if (response.action === 'unliked'){
                    icon.html('favorite_border')
                    if (likes || likes==0) {like_count.html(likes - 1)}
                }
            }
        });
    });

    //Like Comment AJAX
    $("main").on('click', ".comment-likes", function(){
        var like_count = $(this).find('h5')
        var icon = $(this).find('i')
        var id = parseInt($(this).parents('.commentContainer').attr('id'))
        $.ajax({
            url: '/api/likeComment',
            type: "PUT",
            DataType: "json",
            data: {'comment_id': id},

            success: function(response){
                if (response.action==='error') {return} 

                likes = Number(like_count.html())
                if (response.action === 'liked'){
                    icon.html('favorite')
                    if (likes || likes==0) {like_count.html(likes + 1)}
                } else if (response.action === 'unliked'){
                    icon.html('favorite_border')
                    if (likes || likes==0) {like_count.html(likes - 1)}
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
              
                var followerCount = $('.follower-count')
                followers = Number(followerCount.html())
                if ($followButton.html().trim() === "Follow"){
                    $followButton.html("Following")
                    if (followers || followers==0) {followerCount.html(followers + 1)}
                } else {
                    $followButton.html("Follow")
                    if (followers || followers==0) {followerCount.html(followers - 1)}
                }

                $followButton.toggleClass('account-following')
                $followButton.toggleClass('account-button')
                $followButton.toggleClass('following')
                $followButton.toggleClass('follow')  

            }
        });
    }

    //Follow/Unfollow recommended accounts
    $('#unfollowRecommendedButton').click(FollowRecommended)

    $('#rightbar').on('click', '.recommendedFollowButton', function(e){
        var followButton = $(e.target)
        if (followButton.hasClass('follow')){
            FollowRecommended(e)
        } else if (followButton.hasClass('following')){
            userRecommended = $('#' + followButton.val() + '-Recommended')
            username = userRecommended.children('.recommendedUsername').html()
            $('#unfollowRecommendedButton').val(followButton.val())
            $('#unfollowRecommendedModalLabel').html('Unfollow ' + username + '?') 
            $('#unfollowRecommendedModal').modal('show')
        }
    });
    $('#rightbar').on('mouseenter', '.recommendedFollowButton', function(e){
        var followButton = $(e.target)
        if (followButton.hasClass('following')){
            followButton.html("Unfollow?")
            followButton.removeClass("account-following")
            followButton.addClass("account-unfollow") 
        }
    });
    $('#rightbar').on('mouseleave', '.recommendedFollowButton', function(e){
        var followButton = $(e.target)
        if (followButton.hasClass('following')){
            followButton.html("Following")
            followButton.addClass("account-following")
            followButton.removeClass("account-unfollow") 
        }    
    });

    function FollowRecommended(e){
        var followButton = $(e.target)
        var follow_id = followButton.val()
        if (!followButton.hasClass('recommendedFollowButton')){
            followButton = $('#' + follow_id + '-Recommended').find('.recommendedFollowButton') 
        }
        $.ajax({
            url: '/api/follow',
            type: "PUT",
            DataType: "json",
            data: {'user_id': follow_id},

            success: function(response){
                if (response.action==='error') {return} 
    
                userRecommended = $('#' + follow_id + '-Recommended')
                var followerCount = userRecommended.find('.recommendedFollowers')
                followers = Number(followerCount.html().split(' ')[0])
                if (followButton.html().trim() === "Follow"){
                    followButton.html("Following")
                    if (followers || followers==0) {followerCount.html(followers + 1 + " Followers")}
                } else {
                    followButton.html("Follow")
                    if (followers || followers==0) {followerCount.html(followers - 1 + " Followers")}
                }

                followButton.toggleClass('account-following')
                followButton.toggleClass('account-button')
                followButton.toggleClass('following')
                followButton.toggleClass('follow')  

            }
        }); 
    }

    //Like and Comment Hover CSS
    $("main").on("mouseenter mouseleave", ".post-stats", function(e){
        var $stat = $(e.currentTarget)
        var $icon = $stat.find('.post-icon')
        if ($stat.hasClass('post-comment')){
            $stat.toggleClass('comment-hover')
        } else if ($stat.hasClass('post-like')){
            $stat.toggleClass('like-hover')
        }
    });

    $("main").on("mouseenter mouseleave", ".comment-likes", function(e){
        var $stat = $(e.currentTarget)
        $stat.toggleClass('like-hover')
    });

    //Search Logic
    var searchType = 'users'
    var searchBar = $('#searchBar')

    if (contentType == 'search'){
        var UsersSearchScript = document.querySelector('#UsersSearch-template')
        if (UsersSearchScript){
            var usersTemplate = Handlebars.compile(UsersSearchScript.innerHTML) 
        } 
        var PostsSearchScript = document.querySelector('#PostsSearch-template')
        if (UsersSearchScript){
            var postSearchTemplate = Handlebars.compile(PostsSearchScript.innerHTML) 
        } 
    }

    searchBar.keyup(searchAPI)

    function searchAPI(){
        var searchBody = $('.searchBody')
        var searchString = searchBar.val()
        if (searchString){
            $.ajax({
                url: '/api/search',
                type: "POST",
                DataType: "json",
                data: {'searchType': searchType, 'searchString': searchString},

                success: function(data){
                    searchBody.empty()
                    if (data.results=='noposts'){
                        var noresults = $('<h3>').addClass('noresults').html('No Results')
                        searchBody.append(noresults)
                        return
                    }
                    if (searchType == 'users'){
                        data.results.forEach(function(user, i){
                            var User = usersTemplate(user)
                            searchBody.append(User) 
                        })
                    } else if (searchType == 'posts'){
                        data.results.forEach(function(post, i) {
                            var Post = postSearchTemplate(post)
                            searchBody.append(Post)  
                        })
                    }
                }
            })
        } else {
            searchBody.empty()
        }
    }

    $(".searchType").click(function(){
        if (this.id == 'searchUsers'){
            if(searchType == 'users'){return}
            searchType = 'users'
            searchBar[0].placeholder = 'Search for users...'
        }else if (this.id == 'searchPosts'){
            if(searchType == 'posts'){return}
            searchType = 'posts'
            searchBar[0].placeholder = 'Search for posts...'
        }
        searchAPI()
        $("#searchUsers").toggleClass('searchType-active')
        $("#searchPosts").toggleClass('searchType-active')
    });


    //Delete Post API
    $('main').on('click', '.deletePost', function(e){
        $('#deletePostModal').modal('show')
        $('#deletePostButton')[0].value = $(e.target).closest('.post-container')[0].id 
    });

    $('#deletePostButton').click(function(e){
        var post_id = $(e.target).val()
        console.log(post_id)
        $.ajax({
            url: '/api/delete_post',
            type: "DELETE",
            DataType: "json",
            data: {'post_id': post_id},

            success: function(data){
                if (data.action == 'deleted'){
                    $('#'+post_id).remove()

                    var post_count = $('.totalPostCount')
                    posts = Number(post_count.html())
                    if (posts || posts==0) {post_count.html(posts - 1)} 
                } 
            }
        })
    })

    //Delete Comments
    $('main').on('click', '.deleteComment', function(e){
        $('#deleteCommentModal').modal('show')
        $('#deleteCommentButton')[0].value = parseInt($(e.target).closest('.commentContainer')[0].id)
    });

    $('#deleteCommentButton').click(function(e){
        var comment_id = $(e.target).val()
        $.ajax({
            url: '/api/delete_comment',
            type: "DELETE",
            DataType: "json",
            data: {'comment_id': comment_id},

            success: function(data){
                if (data.action == 'deleted'){
                    $('#'+comment_id+'-Comment').remove()

                    comment_count = $('.post-comment').find('.post-stats-stat')
                    comments = Number(comment_count.html())
                    if (comments || comments==0) {comment_count.html(comments - 1)} 
                } 
            }
        })
    })


    //Post Comments
    $("#commentButton").click(function(){
        commentContent = $("#CommentInput").val().trim()
        post_id = window.location.pathname.split('/')[2] 
        if(commentContent){
            $.ajax({
                url: '/api/comment',
                type: "POST",
                DataType: "json",
                data: {'post_id': post_id, "content": commentContent},

                success: function(response){
                    if(response.action == 'succesful'){
                    $("#CommentInput")[0].value = ""
                    var comment = commentTemplate(response.comment)
                    $('#commentSection').prepend(comment) 

                    comment_count = $('.post-comment').find('.post-stats-stat')
                    comments = Number(comment_count.html())
                    if (comments || comments==0) {comment_count.html(comments + 1)} 

                    } else if (response.action == 'error'){
                        return
                    }
                }

            })
        }
    });

    //Trigger LogOut Modal
    $('.LogOutButton').click(function(){
        $('#LogOutModal').modal('show')
    });

    $(".addPostChoice").click(function(){
        if($('.postChoice3').hasClass('hiddenPostChoice')){
            $('.postChoice3').removeClass('hiddenPostChoice')
            $(".removePostChoice")[0].disabled = false  
        } else if($('.postChoice4').hasClass('hiddenPostChoice')){
            $('.postChoice4').removeClass('hiddenPostChoice') 
            $(".addPostChoice")[0].disabled = true 
        } 
    });

    $(".removePostChoice").click(function(){
        if(!$('.postChoice4').hasClass('hiddenPostChoice')){
            $('.postChoice4').addClass('hiddenPostChoice') 
            $('.postChoice4').children('input').val('')
            $(".addPostChoice")[0].disabled = false 
        } else if(!$('.postChoice3').hasClass('hiddenPostChoice')){
            $('.postChoice3').addClass('hiddenPostChoice')
            $('.postChoice3').children('input').val('') 
            $(".removePostChoice")[0].disabled = true  
        }  
    });

    //Redirecting Search Results
    $('.searchBody').on('click', '.searchResults', function(e){
        if($(this).children().hasClass('searchUser')){
            username = $(this).find('.searchUsername-user').html()
            window.location.href = '/account/' + username
        }else if($(this).children().hasClass('searchPost')){
            post_id = parseInt($(this).children().attr('id'))
            window.location.href = '/post/' + post_id
        }
    });





    //create users
    $('#doesntexist').click(function(){
        $.ajax({
            url: '/static/usernames.js',
            type: 'GET',
            DataType: "json",

            success: function(data){
                $.ajax({
                    url: '/api/createUsers',
                    type: 'POST',
                    DataType: "json",
                    data: {'data': data},

                    success: function(response){
                        console.log(response.action)
                    }
                })
            } 
        })
    })
});