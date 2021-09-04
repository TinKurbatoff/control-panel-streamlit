import streamlit as st
import streamlit.report_thread as ReportThread
from streamlit.server.server import Server

import datetime as dt
import base64
import logging
# import SessionState

##############################################
############# ENABLE LOGGING #################
##############################################
# create logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'{__file__}.log', 
                    level=logging.INFO, 
                    format = '%(asctime)s: /%(name)s/ %(levelname)s: %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger.setLevel(logging.DEBUG) # ALWAYS DEBUG in FILE
# create console handler and set level to debug
lg = logging.StreamHandler()
lg.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter(fmt='%(asctime)s: /%(name)s/ %(levelname)s: %(message)s', 
                            datefmt='%m/%d/%Y %I:%M:%S %p')
# add formatter to secondary logger
lg.setFormatter(formatter)
# add ch to logger
logger.addHandler(lg) # when call logger both will destinations will be filled
#######################################



##### ———————————————————— Session State part ————————————————————————

"""Hack to add per-session state to Streamlit.
Usage
-----
>>> import SessionState
>>>
>>> session_state = SessionState.get(user_name='', favorite_color='black')
>>> session_state.user_name
''
>>> session_state.user_name = 'Mary'
>>> session_state.favorite_color
'black'
Since you set user_name above, next time your script runs this will be the
result:
>>> session_state = get(user_name='', favorite_color='black')
>>> session_state.user_name
'Mary'
"""
try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
except Exception:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server



class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.
        Parameters
        ----------
        **kwargs : any
            Default values for the session state.
        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    def set(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        return

    def get(**kwargs):
        """Gets a SessionState object for the current session.
        Creates a new object if necessary.
        Parameters
        ----------
        **kwargs : any
            Default values you want to add to the session state, if we're creating a
            new one.
        Example
        -------
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        ''
        >>> session_state.user_name = 'Mary'
        >>> session_state.favorite_color
        'black'
        Since you set user_name above, next time your script runs this will be the
        result:
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        'Mary'
        """
        # Hack to get the session object from Streamlit.

        ctx = ReportThread.get_report_ctx()

        this_session = None

        current_server = Server.get_current()
        if hasattr(current_server, '_session_infos'):
            # Streamlit < 0.56
            session_infos = Server.get_current()._session_infos.values()
        else:
            session_infos = Server.get_current()._session_info_by_id.values()

        for session_info in session_infos:
            s = session_info.session
            if (
                # Streamlit < 0.54.0
                (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
                or
                # Streamlit >= 0.65.2
                (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
            ):
                this_session = s

        if this_session is None:
            raise RuntimeError(
                "Oh noes. Couldn't get your Streamlit Session object. "
                'Are you doing something fancy with threads?')

        # Got the session object! Now let's attach some state into it.

        if not hasattr(this_session, '_custom_session_state'):
            this_session._custom_session_state = SessionState(**kwargs)

        return this_session._custom_session_state

    def get_headers():
        # Hack to get the session object from Streamlit.
        current_server = Server.get_current()
        if hasattr(current_server, '_session_infos'):
            # Streamlit < 0.56
            session_infos = Server.get_current()._session_infos.values()
        else:
            session_infos = Server.get_current()._session_info_by_id.values()

        # Multiple Session Objects?
        for session_info in session_infos:
            headers = session_info.ws.request.headers
            # st.write(headers)
        return headers


##### ———————————————————— Splash screen ————————————————————————

def logo_html(logo_file, logo_width='', logo_text='', logo_shadow=False):    
    
    if logo_shadow:
        logo_shadow_css = 'box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);'
    else: 
        logo_shadow_css = None
    logo_markup = f"""
        <style> .container {{ display: flex;  }}
        .logo-text {{
            font-weight:500 !important;
            font-size:30px !important;
            color: #f9a01b !important;
            padding-top: 75px !important;
        }} .logo-img {{ float:right; width: {logo_width}; {logo_shadow_css} }} </style>
        """
        
    try:
        image_data = base64.b64encode(open(logo_file, "rb").read()).decode()
    except Exception as e:
        logger.info(e)
        image_data = None

    logo_text_markup = f"""
        <div class="container">
            <img class="logo-img" src="data:image/png;base64,{image_data}">
            <p class="logo-text">&nbsp;{logo_text}</p>
        </div>
        """
    return logo_markup + logo_text_markup


def get_session_id():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_info_by_id.items()

    for session_id, session_info in session_infos:
        s = session_info.session
        # st.write(session_info.ws)
        # st.write(f'{s.enqueue}') #== ctx.enqueue)
        # st.write(f'{ctx.enqueue}')
        if (
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            # Streamlit < 0.54.0
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
            or
            # Streamlit >= 0.65.2
            (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
        ):
            session = session_id #session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')

    return id(session)



def ask_password(password_text='',logo_file='',logo_width='',logo_text='', logo_shadow=False, reset=False):
    # password_paceholder = st.empty()
    # password = password_paceholder.text_input('Password','Optimum')
    # if not password == 'OptimalPath':
    #     # st.info("Please enter a valid password")
    #     return
    allowed_ip = ['192.168.2.11']

    session_state = SessionState.get(password_empty=True)
    headers = SessionState.get_headers()
    user_ip = headers.get("X-Real-Ip", None)
    # st.write(user_ip)

    if reset:
        session_state.set(password_empty=True)
        return False # Password check failed
    logo_paceholder = st.empty()
    logo_paceholder.markdown(logo_html(logo_file=logo_file, logo_width=logo_width, logo_text=logo_text, logo_shadow=logo_shadow), unsafe_allow_html=True)

    ## also check IP 
    with open("logging_ip.txt","a") as f:
        # st.write(f"{dt.datetime.now()}| IP:{user_ip}\n")
        f.write(f"{dt.datetime.now()}| IP:{user_ip}\n")
        ## save IP        
    with open("logging_ip.log","a") as f:        
        f.write(f"{dt.datetime.now()}| IP:{user_ip}\n")
    # if user_ip not in allowed_ip:
        # return False


    session_id = get_session_id()
    password_paceholder = st.empty()

    password = password_paceholder.text_input('Password',f'{session_id}')
    if password != password_text and session_state.password_empty: # password wrong AND it has not ever typed correctly
        st.info("Please enter a valid password")
        return False # Password check failed
    else: 
        session_state.password_empty = False; # disable 'password wrong' for this particular session only
        password_paceholder.empty()
        logo_paceholder.empty()

    return True # Password check ok


if __name__ == '__main__':
    print('This is module for Streamlit web app to show a splash screen')

