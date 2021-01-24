from django.urls import reverse, reverse_lazy

FIRST_GROUP_NAME = "test-group-1"
FIRST_GROUP_SLUG = "test-slug-1"
FIRST_GROUP_DESCRIPTION = "test-description-1"
SECOND_GROUP_NAME = "test-group-2"
SECOND_GROUP_SLUG = "test-slug-2"
SECOND_GROUP_DESCRIPTION = "test-description-2"
USERNAME = "test-user"
FOLLOWER = "test-follower"
POST_TEXT = "test-post"
POST_NEW_TEXT = "test-edit-post"
COMMENT_TEXT = "test-comment"
FIRST_IMG_NAME = "img-1"
SECOND_IMG_NAME = "img-2"

INDEX_URL = reverse("index")
SIGNUP_URL = reverse_lazy("login")
NEW_POST_URL = reverse("new_post")
FOLLOW_INDEX_URL = reverse("follow_index")
AUTHOR_URL = reverse("about:author")
TECH_URL = reverse("about:tech")
PAGE_NOT_FOUND_URL = reverse("404")
SERVER_ERROR_URL = reverse("500")

FIRST_GROUP_URL = reverse("group", args=[FIRST_GROUP_SLUG])
SECOND_GROUP_URL = reverse("group", args=[SECOND_GROUP_SLUG])
PROFILE_URL = reverse("profile", args=[USERNAME])
FOLLOWER_URL = reverse("profile", args=[FOLLOWER])
PROFILE_FOLLOW_URL = reverse("profile_follow", args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse("profile_unfollow", args=[USERNAME])

NOT_URL = "not" + PAGE_NOT_FOUND_URL

INDEX_TEMPLATE = "index.html"
NEW_POST_TEMPLATE = "posts/new_post.html"
FOLLOW_INDEX_TEMPLATE = "posts/follow.html"
GROUP_TEMPLATE = "posts/group.html"
PROFILE_TEMPLATE = "posts/profile.html"
POST_TEMPLATE = "posts/post.html"
POST_EDIT_TEMPLATE = "posts/new_post.html"
PAGE_NOT_FOUND_TEMPLATE = "misc/404.html"
AUTHOR_TEMPLATE = "about/author.html"
TECH_TEMPLATE = "about/tech.html"

NEW_GUEST_TARGET_URL = SIGNUP_URL + "?next=" + NEW_POST_URL
FOLLOW_INDEX_GUEST_TARGET_URL = SIGNUP_URL + "?next=" + FOLLOW_INDEX_URL
PROFILE_FOLLOW_GUEST_TARGET_URL = SIGNUP_URL + "?next=" + PROFILE_FOLLOW_URL
PROFILE_UNFOLLOW_GUEST_TARGET_URL = (SIGNUP_URL +
                                     "?next=" + PROFILE_UNFOLLOW_URL)
PROFILE_FOLLOW_USER_TARGET_URL = PROFILE_URL
PROFILE_FOLLOW_FOLLOWER_TARGET_URL = PROFILE_URL
PROFILE_UNFOLLOW_USER_TARGET_URL = PROFILE_URL
PROFILE_UNFOLLOW_FOLLOWER_TARGET_URL = PROFILE_URL

FIRST_IMG = (b"\x47\x49\x46\x38\x39\x61\x02\x00"
             b"\x01\x00\x80\x00\x00\x00\x00\x00"
             b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
             b"\x00\x00\x00\x2C\x00\x00\x00\x00"
             b"\x02\x00\x01\x00\x00\x02\x02\x0C"
             b"\x0A\x00\x3B")
