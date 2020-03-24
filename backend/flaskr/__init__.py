import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request,selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  questions_per_page = questions[start:end]
  return questions_per_page

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
 
  #This endpoint handles GET requests for all available categories
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    c_dict = {}
    for category in categories:
      c_dict[category.id]=category.type    
    if (len(c_dict) == 0):
      abort(404)

    return jsonify({
        'success':True,
        'categories':c_dict
    })

  #This endpoint handles GET requests for questions
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    questions_per_page = paginate_questions(request, questions)
    
    if (len(questions_per_page) == 0):
      abort(404)

    categories = Category.query.all()
    c_dict={}
    for category in categories:
      c_dict[category.id]=category.type

    return jsonify({
        'success':True,
        'questions':questions_per_page,
        'total_questions':len(questions),
        'categories':c_dict
    })
  
  #This endpoint deletes question using a question ID
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()

      if question is None:
        abort(404)
      
      question.delete()
      questions = Question.query.all()
      questions_per_page = paginate_questions(request,questions)

      return jsonify({
          'success':True,
          'deleted':question_id,
          'questions':questions_per_page,
          'total_questions':len(questions),
      })

    except:
      abort(422)
  
  #This endpoint POST a new question
  @app.route('/questions', methods = ['POST'])
  def create_question():
    body = request.get_json()


    question = body.get('question')
    print("okoko")
    print(question)
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')
    if question is None or answer is None or difficulty is None or category is None:
      abort(422)
    try:
      new_question = Question(question=question, answer=answer, 
                              difficulty=difficulty, category=category)
    
      new_question.insert()

      questions = Question.query.all()
      questions_per_page = paginate_questions(request, questions)

      return jsonify({
          'success':True,
          'created': new_question.id,
          'question_created': new_question.question,
          'questions': questions_per_page,
          'total_questions':len(questions)
      })
    except:
      abort(422)
  
  #This endpoint gets questions based on a search term
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()

    search_term = body.get('searchTerm')
   
    if search_term:
      search_results = Question.query.filter(Question.question.ilike('%{value}%'.format(value=search_term))).all()
      if len(search_results) == 0:
        abort(404)
      return jsonify({
        'success': True,
        'questions': [result.format() for result in search_results],
        'totalQuestions': len(search_results),
        'currentCategory': None
      })
    else:
      abort(404)

  #This endpoint gets question based on category
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    try:
      ids = []
      categories = Category.query.with_entities(Category.id).all()
      for (id,) in categories:
        ids.append(id)
      
      if category_id not in ids:
        abort(404)
      questions = Question.query.filter(
                Question.category == str(category_id)).all()
      print(questions)
      return jsonify({
        'success': True,
        'questions':[question.format() for question in questions],
        'total_question': len(questions),
        'current_category': category_id
      })
    except:
      abort(404)


  #This is a POST endpoint to get questions to play the quiz
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    
    previousQuestions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')
    
    if quiz_category is None:
      abort(400)
    questions = None
    id = (quiz_category['id'])
    if id !=0:
      questions = Question.query.filter(Question.category == str(id)).all()
    else:
      questions = Question.query.all()
    
    if previousQuestions != None:
      for question in questions:
        if question.id not in previousQuestions:
          return jsonify({
            'success': True,
            'question': question.format()
          })
    else:
      return jsonify({
        "success": True,
        'question': questions[0].format()
      })
    
  
  #Error handlers for errors 404, 400 and 422
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found"
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
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    })
  return app