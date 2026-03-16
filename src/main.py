from fastapi import FastAPI
from src.users.router import router as router_users
from src.posts.routers.posts import router as router_posts
from src.posts.routers.categories import router as router_categories
from src.posts.routers.tags import router as router_tags
from src.posts.routers.comments import router as router_comments


app = FastAPI(
    title="MyBlog",
    security=[{"BearerAuth": []}]
)


@app.get("/", tags=["Системные эндпоинты"], summary="Проверка сервера")
async def root():
    return {"message": "Hello world!"}


app.include_router(router_users)
app.include_router(router_posts)
app.include_router(router_categories)
app.include_router(router_tags)
app.include_router(router_comments)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)