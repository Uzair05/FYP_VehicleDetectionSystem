import streamlit as st
import os

def main():
    st.write("# Stolen Vehicle Detection Dashboard")
    st.write("<<Introduction>>")

    uploaded_video = st.file_uploader("Video To Analyze", type=["mp4", "mkv", "webm"], accept_multiple_files=False,
    help="The video is analyzed by the object detection system for stolen vehicles",label_visibility="visible")

    if uploaded_video is not None:
        # To read file as bytes:
        # bytes_data = uploaded_video.getvalue()
        # st.video(bytes_data)
        if os.path.exists("./Tmp"):
            os.system("rm -rf ./Tmp")
        os.mkdir("./Tmp")
        with open(os.path.join("Tmp",uploaded_video.name),"wb") as f:
            f.write(uploaded_video.getbuffer())
            
    

        

if __name__ == "__main__":
    main()