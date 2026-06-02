import streamlit as st
import subprocess

def render_factory_trigger():
    st.subheader('?? AI Factory Control')
    if st.button('Trigger Factory Task (deploy)'):
        st.write('Running factory task...')
        try:
            res = subprocess.run(['python', 'run_task.py', 'deploy'], capture_output=True, text=True)
            st.text_area('Execution Log:', value=res.stdout + res.stderr, height=300)
        except Exception as e:
            st.error(f'Error: {e}')
