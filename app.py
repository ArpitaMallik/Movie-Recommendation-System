import pandas as pd
import streamlit as st
import pickle
import requests

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=9bd2fffbebd1f5b32927fc66591c22b4')
    data = response.json()
    return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']

def fetch_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=9bd2fffbebd1f5b32927fc66591c22b4')
    data = response.json()
    genres = ", ".join([genre['name'] for genre in data['genres']])
    details = {
        "Title": data['title'],
        "Overview": data['overview'],
        "Release Date": data['release_date'],
        "Rating": data['vote_average'],
        "Genres": genres
    }
    return details

def recommend(movie):
    movie_idx = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_idx]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:10]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_ids = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_ids.append(movie_id)
    return recommended_movies, recommended_movies_posters, recommended_movies_ids

# Load data
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommendation System')

selected_movie = st.selectbox(
    "Choose a Movie",
    movies['title'].values
)

if st.button('Recommend'):
    names, posters, ids = recommend(selected_movie)
    st.session_state['names'] = names
    st.session_state['posters'] = posters
    st.session_state['ids'] = ids

if 'names' in st.session_state:
    st.write(f"Top 10 recommendations for {selected_movie}:\n\n")

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(st.session_state['names'][i])
            if st.button("Details", key=f"details_{i}"):
                st.session_state['selected_movie'] = i
            st.image(st.session_state['posters'][i])

    cols = st.columns(5)
    for i in range(5, 10):
        with cols[i - 5]:
            st.text(st.session_state['names'][i])
            if st.button("Details", key=f"details_{i}"):
                st.session_state['selected_movie'] = i
            st.image(st.session_state['posters'][i])

if 'selected_movie' in st.session_state:
    details = fetch_details(st.session_state['ids'][st.session_state['selected_movie']])
    st.markdown(f"# Movie Details: \n")
    st.markdown(f"## {details['Title']}")
    st.write(f"**Genres:** {details['Genres']}")
    st.write(f"**Overview:** {details['Overview']}")
    st.write(f"**Release Date:** {details['Release Date']}")
    st.write(f"**Rating:** {details['Rating']}")
    st.image(st.session_state['posters'][st.session_state['selected_movie']])
