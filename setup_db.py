from app import routes, models, db
from app.models import User, Post

db.create_all()

user = User(username="a", email="test@test.com")
user.set_password("b")
db.session.add(user)


post = Post(text_jp="その取っ手を右にねじると箱は開きます。",
            text_en="Twist that knob to the right and the box will open.",
            notes="https://jisho.org/word/%E7%AE%B1",
            user_id=user.get_id())
db.session.add(post)

db.session.commit()
