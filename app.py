from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from markupsafe import escape

app = Flask(__name__)
# SQLite数据库，文件存本地lab.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "lab‑secret‑demo‑key‑998877"

db = SQLAlchemy(app)
jwt = JWTManager(app)

# 用户数据表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)

# 创建数据库，自动生成测试账号 admin / 密码123456
with app.app_context():
    db.create_all()
    user = User.query.filter_by(username="admin").first()
    if not user:
        hash_password = bcrypt.hashpw(b"123456", bcrypt.gensalt())
        new_user = User(username="admin", password_hash=hash_password)
        db.session.add(new_user)
        db.session.commit()

# 接口1 POST /auth/login 用户登录
@app.route("/auth/login", methods=["POST"])
def login():
    json_data = request.get_json()
    username = json_data.get("username")
    password = json_data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode("utf‑8"), user.password_hash):
        token = create_access_token(identity=username)
        return jsonify(access_token=token), 200
    return jsonify(message="用户名或密码错误"), 401

# 接口2 GET /api/data 需要JWT鉴权
@app.route("/api/data", methods=["GET"])
@jwt_required()
def api_data():
    current_username = get_jwt_identity()
    user_controlled_input = "<script>alert('xss测试')</script>测试用户内容"
    safe_output = escape(user_controlled_input) # XSS转义防护
    resp_data = {
        "login_user": current_username,
        "data": [{"id": 1,"content": safe_output},{"id":2,"content":"第二篇文章"}]
    }
    return jsonify(resp_data)

# 接口3【自定义接口】GET /api/profile 获取当前用户资料
@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user = get_jwt_identity()
    return jsonify(username=user, note="自定义接口，用户个人资料")

if __name__ == "__main__":
    app.run(debug=True)
