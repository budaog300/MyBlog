query = (
    select(User)
    .options(joinedload(User.profile))
    .where(       
        select(func.count(Post.id))
        .where(Post.user_id == User.id)
        .scalar_subquery()
        > 3
    )
)

stmt = (
    delete(Comment)
    .where(
        Comment.post_id.in_(
        select(Post.id)
        .join(Category)
        .where(Category.name == "Spam")
        )
    )
)