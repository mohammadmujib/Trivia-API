import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    # CORS(app)


  
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

   	
    #=== Categories ====
    
  	
    @app.route('/categories')
    def get_categories():
	
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(categories)
        })

    
	 
     #==== Get Questions ====
    
	
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': None,
            'categories': formatted_categories
        })

    # ==== Delete Question ====
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
            })
        except:
            abort(422)

    #===== Post Questions =====
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    #==== Search Question ====
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        search_term = body.get('searchTerm')
        search_results = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_term))).all()
        current_questions = paginate_questions(request, search_results)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(search_results),
            'current_category': None,
        })


	
    #====GET Question by Category ====
    
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            selection = Question.query.filter(
                Question.category == category_id).order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()
            formatted_categories = {
                category.id: category.type for category in categories}

            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(current_questions),
                'current_category': category_id,
                'categories': formatted_categories
            })
        except:
            abort(422)

   	
    #==== Quizzes ====
    
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        category_data = body.get('quiz_category')
        previous = body.get('previous_questions')

        if ((category_data is None) or (previous is None)):
            abort(400)

        if category_data['id'] == 0:
            questions = Question.query.all()

        else:
            questions = Question.query.filter_by(
                category=category_data['id']).all()

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        question = get_random_question()

        return jsonify({
            'success': True,
            'question': question.format()
        })
  
    #==== error Handler ===
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
