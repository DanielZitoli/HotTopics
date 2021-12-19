$(document).ready(function(){
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
    $('.follow').click(FollowAPI)
    $('.unfollowAccount').click(FollowAPI)

    function FollowAPI(e){
        var $followButton = $(e.target)
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
    
    $('.following').hover(hoverUnfollow);

    function hoverUnfollow(e){
        var $followButton = $(e.target)

        if ($followButton.html().trim() == "Following"){
            $followButton.html("Unfollow?")
        } else {
            $followButton.html("Following")
        } 

        $followButton.toggleClass("account-following")
        $followButton.toggleClass("account-unfollow")
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