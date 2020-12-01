def on_enter(event_data):
    """ """
    pocs = event_data.model

    # Clear any current observation
    pocs.observatory.current_observation = None

    pocs.next_state = 'parked'

    pocs.say("I'm closing the dome.")
    # This currently closes the shutter only!
    pocs.observatory.dome.close_dome()
    pocs.say("I'm takin' it on home and then parking.")
    pocs.observatory.mount.home_and_park()
