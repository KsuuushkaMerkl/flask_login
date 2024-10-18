import json

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import TypePerson, Counterparties, Base

from db import Session, engine

app = Flask(__name__)

app.secret_key = 'FIygzXJEsIuAV6RVfgNSS/7rjK1gZWRpSUc4//vIt0mFYcK6RBFeOF1Y5YFd4AlsLDZuKn5OrAmTCO7a0hEnTQ=='

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users_db = {
    'user@example.com': generate_password_hash('password123')
}


class User(UserMixin):
    def __init__(self, email):
        self.id = email


@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users_db else None


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/get/login/content', methods=['GET'])
def get_login_content():
    return render_template('form.html')


@app.route('/login', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']

    if email in users_db and check_password_hash(users_db[email], password):
        user = User(email)
        login_user(user)
        return redirect(url_for('dashboard'))
    return 'Invalid credentials', 401


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({"message": "Welcome to the dashboard!", "user": current_user.id})


@app.route('/counterparties', methods=['GET'])
def get_counterparties():
    session = Session()
    try:
        results = session.query(
            Counterparties.id,
            Counterparties.internal_name,
            TypePerson.value.label('type'),
            Counterparties.heads
        ).join(TypePerson).filter(
            Counterparties.active.is_(True)
        ).order_by(
            TypePerson.value.asc(),
            Counterparties.internal_name.asc()
        ).all()

        counterparties_list = []
        for row in results:
            heads = row.heads
            current_head = list(json.loads(heads).keys())[0] if heads else None

            counterparties_list.append({
                'id': row.id,
                'internal_name': row.internal_name,
                'type': row.type,
                'current_head': current_head
            })

        return jsonify(counterparties_list)
    finally:
        session.close()


@app.route('/counterparties/<string:inn>/banks', methods=['GET'])
def get_banks_by_inn(inn):
    session = Session()
    try:
        counterparty = session.query(Counterparties).filter(
            Counterparties.INN == inn,
            Counterparties.active.is_(True)
        ).first()

        if not counterparty:
            abort(404, description="Counterparty not found")

        return jsonify(json.loads(counterparty.banks))
    finally:
        session.close()


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def prepare_db():
    session = Session()

    Base.metadata.create_all(engine)

    type_persons = [
        TypePerson(value='Юр. лицо'),
        TypePerson(value='Физ. лицо')
    ]

    counterparties_data = [
        Counterparties(
            internal_name='Компания 1',
            INN='5073530173',
            KPP='504120546',
            OGRN='5644193644208',
            heads='{"Петров Евгений Васильевич": {"position": "Генеральный директор", "surname": "Петров", "first_name": "Евгений", "middle_name": "Васильевич", "sex": "male", "act_upon": "Устава", "from_date_of": "2009-11-16", "up_to_date_of": ""}}',
            banks='{"Банк ВТБ": {"account": "46235285108075356324", "name": "Банк ВТБ", "corr_account": "82456846202400480848", "bik": "715493251"}}',
            full_name='Общество с ограниченной ответственностью "Компания Первых"'
        ),
        Counterparties(
            internal_name='Компания Егора',
            INN='5091475412',
            KPP='506193519',
            OGRN='2883519172040',
            heads='{"Поддубный Егор Дмитрович": {"position": "Директор", "surname": "Поддубный", "first_name": "Егор", "middle_name": "Дмитрович", "sex": "male", "act_upon": "Устава", "from_date_of": "2012-10-01", "up_to_date_of": ""}}',
            banks='{"Банк СБЕР": {"account": "91423421155207912522", "name": "Банк СБЕР", "corr_account": "03610058264387258146", "bik": "520474627"}, "Альфа Банк": {"account": "63482356472656477742", "name": "Альфа Банк", "corr_account": "95878563565550043241", "bik": 6210064525}}',
            full_name='Общество с ограниченной ответственностью "ПЕДСтрой"'
        )
    ]

    try:
        session.add_all(type_persons)
        session.commit()
    except Exception as e:
        pass

    try:
        session.add_all(counterparties_data)
        session.commit()
    except Exception as e:
        pass
    finally:
        session.close()


if __name__ == '__main__':
    prepare_db()
    app.run(host="0.0.0.0", debug=True)
