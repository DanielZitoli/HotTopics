import secrets
import os
import random
from typing import Type
from PIL import Image
from flask import json, redirect, render_template, request, flash, jsonify, abort, session
from flask.helpers import url_for
from sqlalchemy.orm import session, query
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta

from hottopics import app, db
from hottopics.models import Users, Posts, Comments, Favourites, CommentLikes, Follows, Votes
from hottopics.forms import Registration, LoginForm, UpdateAccount, CreatePost, PasswordChange, LogOut
from hottopics.helpers import display_date


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home")
    return redirect("/login")
    
@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/home")

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if not user:
            user = Users.query.filter_by(email=form.username.data).first()
        if user and check_password_hash(user.hash, form.password.data):
            login_user(user)
            return redirect("/home")
        else:
            flash("Login Unsuccessful, please check username/email and password", 'danger')
    return render_template("login.html", title="Login", form=form)
    
@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect("/home")

    form = Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = Users(username=form.username.data, email=form.email.data, hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/home")
    return render_template("signup.html", title="Sign Up", form=form)

@app.route("/logout")
@login_required
def logout():
    """Signs User Out"""
    logout_user()
    return redirect(url_for('login'))




@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="Home")

@app.route("/following")
@login_required
def following():
    return render_template("home.html", title="Following")

@app.route("/favourites")
@login_required
def favourites():
    return render_template("home.html", title="Favourites")

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    if not post_id:
        abort(400)
    if not type(post_id) is int:
        abort(400)
    post = Posts.query.get(post_id)
    if not post:
        abort(404)
    return render_template("post.html", title="Post")

@app.route("/account/<username>")
@login_required
def account(username):
    if not username:
        abort(400)
    user = Users.query.filter_by(username = username).first()
    if not user:
        abort(404)
    follow = Follows.query.filter_by(follower=current_user.id, following=user.id).first()
    total_votes, post_count = 0, 0
    for post in user.posts:
        total_votes += post.total_votes()
        post_count += 1
    
    stats = [displayNumbers(post_count), displayNumbers(total_votes), displayNumbers(user.followers), displayNumbers(user.following)]
   
    return render_template('account.html', title="Account", user=user, stats=stats, follow=follow, date_joined=display_date(user.joined))

@app.route("/account/settings", methods=["GET", "POST"])
@login_required
def settings():
    settingsForm = UpdateAccount()
    passwordForm = PasswordChange()
    LogOutForm = LogOut()
    if settingsForm.submitAccount.data and settingsForm.validate_on_submit():
        if settingsForm.picture.data:
            picture_file = save_picture(settingsForm.picture.data)
            if current_user.image_file != "default.jpeg":
                remove_picture()
            current_user.image_file = picture_file
        current_user.username = settingsForm.username.data
        current_user.email = settingsForm.email.data
        db.session.commit()
        return redirect("/account/" + current_user.username)
    if passwordForm.submitPassword.data and passwordForm.validate_on_submit():
        newHash = generate_password_hash(passwordForm.new_password.data)
        current_user.hash = newHash
        db.session.commit()
        return redirect(url_for('account', username=current_user.username))
    if LogOutForm.submitLogOut.data and LogOutForm.validate_on_submit():
        return redirect(url_for('logout'))
    if request.method == "GET":
        settingsForm.username.data = current_user.username
        settingsForm.email.data = current_user.email

    return render_template('settings.html', settingsForm=settingsForm, passwordForm=passwordForm, LogOutForm=LogOutForm)

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (150, 150)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def remove_picture():
    picture_path = os.path.join(app.root_path, "static/profile_pics", current_user.image_file) 
    os.remove(picture_path)

@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    PostForm = CreatePost()

    if PostForm.validate_on_submit():
        post = Posts(content=PostForm.content.data, choice_1=PostForm.choice_1.data, choice_2=PostForm.choice_2.data,
        choice_3=PostForm.choice_3.data, choice_4=PostForm.choice_4.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html', title="Create Post", PostForm=PostForm)

@app.route("/search")
@login_required
def search():
    return render_template('search.html', title="Search")

@app.route("/api/loadMorePosts", methods=["GET", "POST"])
@login_required
def loadMorePosts():
    contentType = request.form.get("contentType", type=str)
    if not contentType:
        abort(404)
    accountUsername = request.form.get("accountUsername", type=str)
    pageNum = request.form.get("pageNum", type=int)
    if not pageNum:
        abort(400)

    if contentType == 'home':
        posts = Posts.query.order_by(Posts.posted.desc()).paginate(per_page=10, page=pageNum)
        if not posts.items:
            return jsonify(error='noposts')
    elif contentType == 'following':
        follows = Follows.query.filter_by(follower=current_user.id).all()
        followIDs = []
        for follow in follows:
            followIDs.append(follow.following)
        if not followIDs:
            return jsonify(error='notfollowing')
        posts = Posts.query.filter(Posts.user_id.in_(followIDs)).order_by(Posts.posted.desc()).paginate(per_page=10, page=pageNum)
        if not posts.items:
            return jsonify(error='noposts')
    elif contentType == 'favourites':
        favourites = current_user.favourites
        favouriteIDs = []
        for favourite in favourites:
            favouriteIDs.append(favourite.post)
        if not favouriteIDs:
            return jsonify(error='noposts')
        posts = Posts.query.join(Favourites, Posts.id==Favourites.post).filter(Posts.id.in_(favouriteIDs)).order_by(Favourites.date_added.desc()).paginate(per_page=10, page=pageNum)
    elif contentType == 'account':
        if accountUsername == 'settings':
            return jsonify(error='invalidContentType')
        user = Users.query.filter_by(username=accountUsername).first()
        if not user.posts:
            if current_user == user:
                return jsonify(error='noposts', ownAccount=True)
            else:
                return jsonify(error='noposts', ownAccount=False)
        posts = Posts.query.filter_by(user_id=user.id).order_by(Posts.posted.desc()).paginate(per_page=10, page=pageNum)
    elif contentType == 'post':
        post = None
        if pageNum == 1:
            post = Posts.query.get(accountUsername)
            if not post: 
                abort(404)
            liked_posts = []
            liked = current_user.favourites
            for like in liked:
                liked_posts.append(like.post)
            author = post.author
            total_votes = post.total_votes()
            time_ago = time_since(post.posted)
            percentages = roundedPercentages(post)
            vote = Votes.query.filter_by(user_id=current_user.id, post=post.id).first()
            post = post.as_dict()
            post["author_username"] = author.username
            post["author_image"] = author.image_file
            post["total_votes"] = displayNumbers(total_votes)
            post["likes"] = displayNumbers(post["likes"])
            post["comment_count"] = displayNumbers(post["comment_count"])
            post["is_liked"] = post['id'] in liked_posts
            post["time_since"] = time_ago
            post["percentages"] = percentages
            post["choice"] = vote.choice if vote else False

        comments = Comments.query.filter_by(post_id=accountUsername).order_by(Comments.likes.desc(), Comments.posted.desc()).paginate(per_page=10, page=pageNum)
        liked_comments = []
        for like in CommentLikes.query.filter_by(user_id=current_user.id):
            liked_comments.append(like.comment)
        jsonComments = []
        for comment in comments.items:
            commentInfo = {}
            commentInfo['id'] = comment.id
            commentInfo['content'] = comment.content
            commentInfo['likes'] = displayNumbers(comment.likes)
            commentInfo['posted'] = time_since(comment.posted)
            commentInfo['username'] = comment.author.username
            commentInfo['author_image'] = comment.author.image_file
            commentInfo["is_liked"] = comment.id in liked_comments
            commentInfo['ownComment'] = True if comment.author == current_user else False
            jsonComments.append(commentInfo)
        lastPage = True if comments.page == comments.pages else False
        
        return jsonify(post=post, comments=jsonComments, lastPage=lastPage)
    else:
        return jsonify(error='invalidContentType')

    lastPage = True if posts.page == posts.pages else False
    ownAccount = True if current_user.username == accountUsername else False

    jsonPosts = []
    liked_posts = []

    liked = current_user.favourites
    for like in liked:
        liked_posts.append(like.post)

    posts = posts.items
    for post in posts:
        author = post.author
        total_votes = post.total_votes()
        time_ago = time_since(post.posted)
        percentages = roundedPercentages(post)
        vote = Votes.query.filter_by(user_id=current_user.id, post=post.id).first()
        post = post.as_dict()
        post["author_username"] = author.username
        post["author_image"] = author.image_file
        post["total_votes"] = displayNumbers(total_votes)
        post["likes"] = displayNumbers(post["likes"])
        post["comment_count"] = displayNumbers(post["comment_count"])
        post["is_liked"] = post['id'] in liked_posts
        post["time_since"] = time_ago
        post["percentages"] = percentages
        post["choice"] = vote.choice if vote else False
        jsonPosts.append(post)

    return jsonify(posts=jsonPosts, ownAccount=ownAccount, lastPage=lastPage)


def time_since(date):
    difference = datetime.utcnow()- date
    days = difference.days
    if days >= 365:
        years = int(round(days/365, 0))
        if years == 1:
            return "1 year ago"
        return f"{years} years ago"
    if days >= 30:
        months = int(round(days/30, 0))
        if months == 1:
            return "1 month ago"
        return f"{months} months ago"
    if days >= 7:
        weeks = int(round(days/7, 0))
        if weeks == 1:
            return "1 week ago"
        return f"{weeks} weeks ago"
    if days:
        if days == 1:
            return "1 day ago"
        return f"{days} days ago"

    seconds = difference.seconds
    if seconds >= 3600:
        hours = int(round(seconds/3600, 0))
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"
    if seconds >= 100:
        mins = int(round(seconds/60, 0))
        return f"{mins} mins ago"
    if seconds >= 30:
        return "1 min ago"
    else:
        return "now"

@app.route("/api/like", methods=["PUT"])
@login_required
def like():
    post_id = request.form.get("post_id", type=int)
    if not type(post_id) is int:
        return jsonify(action='error')

    like = Favourites.query.filter_by(user_id=current_user.id).filter_by(post=post_id).first()
    post = Posts.query.get(post_id)
    if post:
        if like:
            db.session.delete(like)
            post.likes = post.likes - 1
            db.session.commit()
            return jsonify(action='unliked')
        else:
            like = Favourites(user_id=current_user.id, post=post_id)
            db.session.add(like)
            post.likes = post.likes + 1
            db.session.commit()
            return jsonify(action='liked')
    else:
        return jsonify(action='error')

@app.route("/api/likeComment", methods=["PUT"])
@login_required
def likeComment():
    comment_id = request.form.get("comment_id", type=int)
    if not type(comment_id) is int:
        return jsonify(action='error')

    like = CommentLikes.query.filter_by(user_id=current_user.id).filter_by(comment=comment_id).first()
    comment = Comments.query.get(comment_id)
    if comment:
        if like:
            db.session.delete(like)
            comment.likes = comment.likes - 1
            db.session.commit()
            return jsonify(action='unliked')
        else:
            like = CommentLikes(user_id=current_user.id, comment=comment_id)
            db.session.add(like)
            comment.likes = comment.likes + 1
            db.session.commit()
            return jsonify(action='liked')
    else:
        return jsonify(action='error')

@app.route("/api/follow", methods=["PUT"])
@login_required
def follow():
    user_id = request.form.get("user_id") 
    user = Users.query.get(user_id)
    if user==current_user:
        abort(404)
    follow = Follows.query.filter_by(follower=current_user.id).filter_by(following=user_id).first()
    if user:
        if follow:
            db.session.delete(follow)
            user.followers = user.followers - 1
            current_user.following = current_user.following - 1 
            db.session.commit()
            return jsonify(action='unfollow')
        else:
            follow = Follows(follower=current_user.id, following=user_id)
            db.session.add(follow)
            user.followers = user.followers + 1
            current_user.following = current_user.following + 1
            db.session.commit()
            return jsonify(action='follow')
    else:
        return jsonify(action='error')

@app.route("/api/vote", methods=["PUT"])
@login_required
def vote():
    post_id = request.form.get("post_id")
    choice = int(request.form.get("choice", int))
    vote = Votes.query.filter_by(user_id=current_user.id).filter_by(post=post_id).first()
    post = Posts.query.get(post_id)
    if post:
        if vote:
            lastVote = vote.choice
            if lastVote == choice:
                return jsonify(action="alreadyvoted")
            if lastVote == 1:
                post.votes_1 = post.votes_1 - 1
            elif lastVote == 2:
                post.votes_2 = post.votes_2 - 1
            elif lastVote == 3:
                post.votes_3 = post.votes_3 - 1
            elif lastVote == 4:
                post.votes_4 = post.votes_4 - 1
            else:
                return jsonify(action='error')
            if choice == 1:
                post.votes_1 = post.votes_1 + 1
            elif choice == 2:
                post.votes_2 = post.votes_2 + 1
            elif choice == 3:
                post.votes_3 = post.votes_3 + 1
            elif choice == 4:
                post.votes_4 = post.votes_4 + 1
            else:
                return jsonify(action='error')
            vote.choice = choice
            db.session.commit()
            return jsonify(action='voted', percentages=roundedPercentages(post), alreadyVoted=True, lastVote=lastVote)
        else:
            vote = Votes(user_id=current_user.id, post=post_id, choice=choice)
            db.session.add(vote)
            if choice == 1:
                post.votes_1 = post.votes_1 + 1
            elif choice == 2:
                post.votes_2 = post.votes_2 + 1
            elif choice == 3:
                post.votes_3 = post.votes_3 + 1
            elif choice == 4:
                post.votes_4 = post.votes_4 + 1
            else:
                return jsonify(action='error')
            db.session.commit()
            return jsonify(action='voted', percentages=roundedPercentages(post), alreadyVoted=False)
    else:
        return jsonify(action='error')

def roundedPercentages(post):
    votes = [post.votes_1, post.votes_2]
    if post.choice_3:
        votes.append(post.votes_3)
    if post.choice_4:
        votes.append(post.votes_4)
    sum = post.total_votes()
    if sum == 0:
        return ""

    percentages = []
    for i in range(0, len(votes)):
        percentages.append([i+1, int((votes[i]/sum*100)//1), (votes[i]/sum)%1])
    sum = 0
    for percentage in percentages:
        sum += percentage[1]
    leftover = 100 - sum
    percentages.sort(key=lambda percentage:percentage[2], reverse=True)
    for i in range(leftover):
        percentages[i][1]+=1
    percentages.sort(key=lambda percentage:percentage[0])
    values = []
    for a,b,c in percentages:
        values.append(b)
    return values

def displayNumbers(number):
    if number > 100000:
        return str(int(round(number/1000, 1))) + 'K'
    if number > 10000:
        return str(round(number/1000, 1)) + 'K'
    if number > 1000:
        return str(round(number/1000, 1)) + 'K'
    return number

@app.route("/api/search", methods=["POST"])
@login_required
def searchResults():
    searchType = request.form.get("searchType")
    searchString = request.form.get("searchString")

    if searchType == 'users':
        users = Users.query.filter(Users.username.ilike(searchString+'%')).order_by(Users.followers.desc()).limit(15).all()
        if len(users) == 15:
            results = [] 
            for user in users:
                result = {}
                result['username'] = user.username
                result['profile_image'] = user.image_file
                result['followers'] = displayNumbers(user.followers)
                results.append(result)
            return jsonify(results=results)

        prevusers_ids = []
        for user in users:
            prevusers_ids.append(user.id)

        wildusers = Users.query.filter(Users.username.ilike('%'+searchString+'%'), Users.id.notin_(prevusers_ids)).order_by(Users.followers.desc()).limit(15-len(users)).all() 
        results = [] 
        for user in users+wildusers:
            result = {}
            result['username'] = user.username
            result['profile_image'] = user.image_file
            result['followers'] = displayNumbers(user.followers)
            results.append(result)
        if results:
            return jsonify(results=results)
        return jsonify(results='noposts')

    if searchType == 'posts':
        posts = Posts.query.filter(Posts.content.ilike('%'+searchString+'%')).order_by(Posts.likes.desc()).limit(10).all()
        results = [] 
        for post in posts:
            result = {}
            result['id'] = post.id
            result['username'] = post.author.username
            result['profile_image'] = post.author.image_file
            result['content'] = post.content
            result['likes'] = displayNumbers(post.likes)
            result['votes'] = displayNumbers(post.total_votes())
            results.append(result)
        if results:
            return jsonify(results=results)
        return jsonify(results='noposts')

@app.route("/api/delete_post", methods=["DELETE"])
@login_required
def deletePost():
    post_id = request.form.get('post_id')
    if not post_id:
        abort(400)
    post = Posts.query.get(post_id)
    if not post:
        return jsonify(action='nopost')
    if not post.author == current_user:
        abort(403)
    
    favourites = Favourites.query.filter_by(post=post.id)
    for favourite in favourites:
        db.session.delete(favourite)

    comments = post.comments
    if comments:
        for comment1 in comments:
            likes = CommentLikes.query.filter_by(comment=comment1.id)
            for like in likes:
                db.session.delete(like)
            db.session.delete(comment1)
    print(comments)
    db.session.delete(post)
    db.session.commit()
    return jsonify(action='deleted')

@app.route("/api/delete_comment", methods=["DELETE"])
@login_required
def deleteComment():
    comment_id = request.form.get('comment_id')
    if not comment_id:
        abort(400)
    comment1 = Comments.query.get(comment_id)
    if not comment1:
        return jsonify(action='nocomment')
    if not comment1.author == current_user:
        abort(403)

    likes = CommentLikes.query.filter_by(comment=comment1.id)
    for like in likes:
        db.session.delete(like)
    
    db.session.delete(comment1)
    post = Posts.query.get(comment1.post_id)
    post.comment_count -= 1

    db.session.commit()
    return jsonify(action='deleted')

@app.route("/api/comment", methods=["POST"])
@login_required
def comment():
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    if not post_id:
        abort(400)
    post = Posts.query.get(post_id)
    if not post:
        return jsonify(action='error')
    comment = Comments(user_id=current_user.id, post_id=post_id, content=content)
    db.session.add(comment)
    post.comment_count += 1
    db.session.commit()

    commentInfo = {}
    commentInfo['id'] = comment.id
    commentInfo['content'] = comment.content
    commentInfo['likes'] = displayNumbers(comment.likes)
    commentInfo['posted'] = time_since(comment.posted)
    commentInfo['username'] = current_user.username
    commentInfo['author_image'] = current_user.image_file
    commentInfo['ownComment'] = True
    commentInfo['is_liked'] = False
    return jsonify(action='succesful', comment=commentInfo)

@app.route("/api/loadSidebar")
@login_required
def loadSidebar():
    my_followings = Follows.query.filter_by(follower=current_user.id).all()
    following_ids = [current_user.id]
    for my_following in my_followings:
        following_ids.append(my_following.following)
    FollowingOfFollowing = {}
    for my_following in my_followings:
        friends_followings = Follows.query.filter_by(follower=my_following.following).filter(Follows.following.notin_(following_ids)).all()
        for user in friends_followings:
            if user.following in FollowingOfFollowing:
                FollowingOfFollowing[user.following] += 1
            else:
                FollowingOfFollowing[user.following] = 1

    recommended = list(sorted(FollowingOfFollowing.items(), key=lambda item: item[1], reverse=True))[:15]
    newRecommended = []
    for rec in recommended:
        newRecommended.append(rec[0])

    if len(newRecommended) < 6:
        extraUsers = Users.query.filter(Users.id.notin_(newRecommended)).filter(Users.id.notin_(following_ids)).order_by(Users.followers.desc()).limit(6-len(newRecommended)).all()
        for user in extraUsers:
            newRecommended.append(user.id)

    users = []
    for row in newRecommended:
        users.append(Users.query.get(row))
    users.sort(key=lambda user: user.followers, reverse=True)

    recommended = []
    for user in users[:6]:
        results = {}
        results['id'] = user.id
        results['username'] = user.username
        results['followers'] = displayNumbers(user.followers)
        results['profile_image'] = user.image_file
        recommended.append(results)

    return jsonify(action='success', recommended=recommended)

def createUsers():
    data = request.form.get('data')
    dictionary = json.loads(data)
    usernames = []
    for row in dictionary:
        usernames.append(row['username'])

    create_users(usernames)
    assign_followers()
    assign_follows()
    return jsonify(action='success')


def create_tests():
    user1 = Users(username="test1", email="Test1@rogers.com", hash="jhvytresdckhcjh")
    user2 = Users(username="test2", email="Test2@gmail.com", hash="jhavscljhqvckjhqvh")
    db.session.add(user1) 
    db.session.add(user2)
    post1 = Posts(content="A tribute to those who got us this far. And an invitation to those who will take us further.", choice_1="yes indeed", choice_2="absolutely", choice_3="yes ", choice_4="no", author=user1) 
    post2 = Posts(content="GOODNIGHT TWITTER BIG DAY TOMORROW", choice_1="haha so true", choice_2="no", choice_3="woah", author=user2)
    post3 = Posts(content="ready for neither trio making top 10. Letssssss go. So good", choice_1="woah really", choice_2="yes for sure", author=user1)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.commit()
    return

def create_users(usernames):
    for username1 in usernames:
        user = Users(username=username1, email="Test1@rogers.com", hash="jhvytresdckhcjh")
        db.session.add(user)
    db.session.commit()
    return

def assign_followers():
    users = Users.query.all()
    for user in users:
        user.followers = random.randint(10, 20000)
    db.session.commit()
    return

def assign_follows():
    users = Users.query.all()
    for user in users:
        for user2 in users:
            if not user == user2:
                if random.randint(10, 20000) % 3 == 0:
                    follow = Follows(follower=user.id, following=user2.id) 
                    db.session.add(follow)
    db.session.commit()
    return

def delete_comments():
    comments = Comments.query.all()
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()
    return
