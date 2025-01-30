from datetime import date

from flask import Flask, jsonify, abort, request
from flask import make_response
from flask_restful import Api, Resource
from flask_restful import reqparse
from flask_restful import inputs
from flask_sqlalchemy import SQLAlchemy

import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)

db.create_all()

parser = reqparse.RequestParser()
# write your code here
api = Api(app)
parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

class EventTodayResource(Resource):
    def get(self):
        events = Event.query.filter(Event.date == date.today()).all()
        app.logger.debug(f"query{events}")
        for event in events:
            app.logger.debug(f"event{event.event}")
        events_list = [
            {"id": event.id, "event": event.event, "date": event.date.strftime('%Y-%m-%d')}
            for event in events
        ]
        return events_list, 200

class EventAddResource(Resource):
    def get(self):
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        app.logger.debug(f"start_time = {start_time}, end_time = {end_time}")
        if start_time and end_time:
            return self.getRange(start_time, end_time)
        events = Event.query.all()
        events_list = [
            {"id": event.id, "event": event.event, "date": event.date.strftime('%Y-%m-%d')}
            for event in events
        ]
        return events_list, 200

    def getRange(self, start_time, end_time):
        events = Event.query.filter(Event.date.between(start_time, end_time)).all()
        events_list = [
            {"id": event.id, "event": event.event, "date": event.date.strftime('%Y-%m-%d')}
            for event in events
        ]
        return events_list, 200

    def post(self):
        args = parser.parse_args()
        event = Event(event=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()
        return {
            "message": "The event has been added!",
            "event": event.event,
            "date": event.date.strftime('%Y-%m-%d')
        }, 200

class EventChangeResource(Resource):
    def get(self, id):
        event = Event.query.get(id)
        if event:
            return {
                "id": event.id,
                "event": event.event,
                "date": event.date.strftime('%Y-%m-%d')
            }, 200
        else:
            abort(404, "The event doesn't exist!")

    def delete(self, id):
        event = Event.query.get(id)
        if event:
            db.session.delete(event)
            db.session.commit()
            return jsonify({"message": "The event has been deleted!"})
        else:
            abort(404, "The event doesn't exist!")


# Füge die Ressource zur API hinzu
api.add_resource(EventTodayResource, '/event/today')
api.add_resource(EventAddResource, '/event')
api.add_resource(EventChangeResource, '/event/<int:id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)
