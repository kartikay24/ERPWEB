import ast
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import mne
import os
from PIL import Image
import ast
import copy
import streamlit as st
import pyrebase
#import streamlit_authenticator as stauth
import streamlit.components.v1 as components
from mne.time_frequency import tfr_morlet
#from obj2html import obj2html
st.set_page_config(page_title="ERP-WEB",layout="wide")

#def obj3D():
    # # 3D view
    # html_string = obj2html("model.obj", html_elements_only=True)
    # components.html(html_string)
    # # Download .obj button
    # with open("model.obj") as f:
    #     st.download_button('Download model.obj', f, file_name="download_name.obj")



def intro():
    st.title("ERP Web")
    st.text("")
    st.write("Welcome to *ERPWeb*,your easy to go solution for creating")
    st.write("**interactive dashboards** for data specifically in .mff format")
    brain=Image.open("brain.jpg")
    st.image(brain)

    st.text("")
    st.markdown("You can upload your custom data from the left sidebar.")
    st.text("")

def Upload_files():
    contents=st.file_uploader(
        "Upload Contents File",
        #type=["mff"],
        accept_multiple_files=True
    )
    mff_files=st.file_uploader(
        "Upload mff Files",
        #type=["mff"],
        accept_multiple_files=True
    )
    for i in contents:
        if i is not None:
            with open(os.path.join("Files.mff/Contents/",i.name),"wb") as t:
                t.write(i.getbuffer())

    for j in mff_files:
        if j is not None:
            with open(os.path.join("Files.mff/",j.name),"wb") as t:
                t.write(j.getbuffer())

@st.cache
def save_plot(raw):
    raw.plot(remove_dc=False)
    plt.savefig('channels.png')

def display_plot():
    rawPlot=Image.open("channels.png")
    st.image(rawPlot)

@st.cache
def save_events(events):
    mne.viz.plot_events(events)
    plt.savefig('events.png')

def display_events():
    rawEvents=Image.open("events.png")
    st.image(rawEvents)

def filter(raw):
    st.subheader("*1) Band Pass Filtering*")
    st.markdown("Manually set the frequencies of interest based on your study")
    st.info("**Delta (0.5 to 4Hz)**, **Theta (4 to 7Hz)**, **Alpha (8 to 12Hz)**, **Sigma (12 to 16Hz)** and **Beta (13 to 30Hz)**")
    freq=st.slider('Frequency Range', 1, 50,(1,30))
    raw.filter(freq[0],freq[1])
    return raw

def apply_ica(raw):
    st.subheader("*2) Artifact Correction*")
    if st.button("Applying ICA"):
        ica=mne.preprocessing.ICA(20,random_state=20)
        ica.fit(raw.copy().filter(8,35))
        #For removing bad channels:Thresholding
        bad_idx,scores=ica.find_bads_eog(raw,'VREF',threshold=2)   #reference channel   #E65 or Cz
        #ica.plot_components(outlines="skirt")
        ica.apply(raw.copy(),exclude=bad_idx).plot()
        return raw

def rereference(raw):
    st.subheader("*3) Rereferencing*")
    reref_page=st.radio("Rereferencing done with respect to:",['Average','VREF'])
    if reref_page=='Average':
        raw=copy.deepcopy(raw).set_eeg_reference('average', projection=True)
    if reref_page=='VREF':
        raw=copy.deepcopy(raw).set_eeg_reference(['VREF'])
    return(raw)
    
def spatial_viz(raw,events,event_ids,op):
    epochs=mne.Epochs(raw,events,event_id=event_ids,tmin=-.5,tmax=1.5,preload=True)
    # epochs=ica.apply(epochs,exclude=ica.exclude)
    #BASELINE
    epochs.apply_baseline((None,0 ))      
    epochs.equalize_event_counts(event_ids)

    #For Creating Dictionary
    data = ["novel","standard","target"]
    n = 10
    st = "target"
    for i in range(1,n):
        data.append(st+str(i))
    
    evokeds={}
    for x in data:
        try:
            value = epochs[x]
            evokeds[x]=value.average()
        except:
            pass
    
    # op=st.selectbox("Select Channel",list(range(0,64)))
             
    mne.viz.plot_compare_evokeds(evokeds,picks=[op]) #33    
    # nc = 64
    # start = "sp"
    # end= ".png"
    # sp=[]
    # for j in range(0,nc):
    #     sp.append(start+str(j)+end)
    plt.savefig('sp'+str(op)+'.png')
    return epochs
    
def display_spatial_viz(op):
    st.image(Image.open('sp'+str(op)+'.png'))

def ERSP(epochs,op):    
    freqs=list(range(3,30))
    tfr_target=tfr_morlet(epochs["target"],freqs,3,return_itc=False)
    tfr_target.plot(picks=[op])
    plt.savefig('timefreq'+str(op)+'.png')

def display_ERSP(op):
    st.image(Image.open('timefreq'+str(op)+'.png'))





def headplot(raw):
    raw.plot_sensors(show_names=True)
    plt.savefig('headplot.png')
    st.image(Image.open('headplot.png'))


    #process_data(df)

    # #1 FILTERING
    # raw.filter(1,30)
    # raw.plot(remove_dc=False)

    # #2 ARTIFACT CORRECTION
    # ica=mne.preprocessing.ICA(20,random_state=20)
    # ica.fit(raw.copy().filter(8,35))
    # #For removing bad channels:Thresholding
    # bad_idx,scores=ica.find_bads_eog(raw,'VREF',threshold=2)   #reference channel   #E65 or Cz
    # print(bad_idx)
    # #ica.plot_components(outlines="skirt")
    # ica.apply(raw.copy(),exclude=bad_idx).plot();

    # #3 REREFERENCING
    # import copy
    # raw=copy.deepcopy(raw).set_eeg_reference(['VREF'])

    # #4 EPOCHING
    # events=mne.find_events(raw)
    # mne.viz.plot_events(events[:len(events)])
    #              INTEGER INPUT

    # event_ids={"standard/stimulus":7,"target/stimulus":8,"novel/stimulus":9} #According to input

    # epochs=mne.Epochs(raw,events,event_id=event_ids,preload=True)
    # epochs=ica.apply(epochs,exclude=ica.exclude)
    # epochs.apply_baseline((None,0 ))
    # epochs.equalize_event_counts(event_ids)

    # epochs.plot()
    # epochs["target"].plot_image(picks=[13])
    # epochs.save("oddball-long-epo.fif",overwrite=True) #Cleaned of bad ICs

    # epochs_for_tfr=mne.Epochs(raw,events,event_id=event_ids,tmin=-.5,tmax=1.5,preload=True) #need longer data segment
    # epochs_for_tfr=ica.apply(epochs_for_tfr,exclude=ica.exclude)
    # epochs_for_tfr.equalize_event_counts(event_ids)

    # epochs_for_tfr.plot()
    # epochs_for_tfr.plot_psd()


def main():

    firebaseConfig = {
        'apiKey': "AIzaSyBhYD9XiQekgFXLuLtPpyp9MDj7LDGByvU",
        'authDomain': "erpweb-991ec.firebaseapp.com",
        'projectId': "erpweb-991ec",
        'storageBucket': "erpweb-991ec.appspot.com",
        'messagingSenderId': "59982596808",
        'appId': "1:59982596808:web:77852572037944c35033fd",
        'measurementId': "G-RFJBM5BSZY",
        'databaseURL':"https://erpweb-991ec-default-rtdb.europe-west1.firebasedatabase.app/"
    }

    intro()
    
    firebase=pyrebase.initialize_app(firebaseConfig)
    auth=firebase.auth()
    db = firebase.database()
    storage = firebase.storage()

    choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

    # Obtain User Input for email and password
    email = st.sidebar.text_input('Please enter your email address')
    password = st.sidebar.text_input('Please enter your password',type = 'password')


    if choice == 'Sign up':
        handle = st.sidebar.text_input('User-name')
        # location=st.sidebar.text_input("Enter Location")
        submit = st.sidebar.button('Create my account')

        if submit:
            user = auth.create_user_with_email_and_password(email, password)
            st.sidebar.success('Your account is created suceesfully!')
            # Sign in
            user = auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Id").set(user['localId'])
            db.child(user['localId']).child("Handle").set(handle)
            
            st.sidebar.info("Please Login to Continue")
            
    if choice == 'Login':
        
        login = st.sidebar.checkbox('Login')
        if login:
            user = auth.sign_in_with_email_and_password(email,password)
            st.sidebar.success("Login Successful")    

            #### AFTER LOGIN ####
            Upload_files()

            #Loading .mff Files
            raw=mne.io.read_raw_egi("Files.mff",preload=True)
            
            #LPF & HPF
            with st.sidebar:
                st.header("Pre-Processing")
                filter(raw)
                apply_ica(raw)
                rereference(raw)


            if st.button("Generate Plot"):
                save_plot(raw)
                display_plot()
            
            st.text("You can view the data and check how it looks for all channels")
            st.text("")


            events=mne.find_events(raw)

            if st.button("Events"):
                save_events(events)
                display_events()
            
            st.text("All the diverse events can be identified and given for further analysis")
            st.text("Add more variables by naming them target2,target3 ...")
            
            x=st.text_input('Event Id for each event:','{"standard/stimulus":7,"target/stimulus":8,"novel/stimulus":9}')
            event_ids=ast.literal_eval(x)


            col1, col2, col3 = st.columns([1,3,1])

            with col1:
                st.write(' ')

            with col2:
                headplot(raw)

            with col3:
                st.write(' ')

            st.text("Manually vizualize graphs for a specific channnel")
            op=st.selectbox("Select Channel",list(range(0,64)))
            epochs_val =spatial_viz(raw,events,event_ids,op)
            st.text("Here we can observe:")

            col1,col2=st.columns(2)
            with col1:
                st.text("the average of all epochs")
                if st.checkbox("Generate Evokeds"):
                    display_spatial_viz(op)
            with col2:  
                st.text("the target spectrogram")  
                if st.checkbox("Generate ERSP"):
                    ERSP(epochs_val,op)
                    display_ERSP(op)
                



if __name__== '__main__' :
    main()
              