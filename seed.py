from app import app
from models import db, User, Feedback

with app.app_context():
    db.drop_all()
    db.create_all()

    u1 = User.register(
        username="LongLegs01",
        password="BarkBark0",
        email="iliketreats@bark.com",
        first_name="Milo",
        last_name="The Puppy"
    )

    u2 = User.register(
        username="GrumpyCat-_-",
        password="GiveMeF00d",
        email="marvin@catnip.corp",
        first_name="Marvin",
        last_name="The Cat"
    )

    u3 = User.register(
        username="ScaredyCat",
        password="WhatAreYouLookingAt300",
        email="george@meow.com",
        first_name="Mojo",
        last_name="The Cat"
    )

    db.session.add_all([u1,u2,u3])
    db.session.commit()


    f1 = Feedback(
        title="Need More Treats",
        content="More pictures of treats plz.",
        username="LongLegs01"
    )

    f2 = Feedback(
        title="More Privacy",
        content="Please leave me alone, how do I unsubscribe???!!!",
        username="GrumpyCat-_-"
    )

    f3 = Feedback(
        title="CALL ME!",
        content="I WANT TO TALK TO A HUMAN!! CALL ME BACK",
        username="GrumpyCat-_-"
    )

    f4 = Feedback(
        title="Nap Times",
        content="Nap times should be long... yawn",
        username="ScaredyCat"
    )

    db.session.add_all([f1,f2,f3,f4])
    db.session.commit()