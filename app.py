from flask import Flask, render_template, flash, redirect
from forms import SearchForm
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'u7PrtQm5Dur0cgkcyOlOmU7kYm9xy4ng'
champions = {}

with open('ChampionDataset.json') as json_file:
    champions = json.load(json_file)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="Home")
    #print(champions[0]["Name"])


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        #TODO Perform tf-idf calculations and return top 5 results
        #Not sure if this does anything.. Would like a toastr message
        flash('Searching...', 'success')
    else:
        flash(f'{form.searchInput} is not valid', 'error')
    return render_template('search.html', title="Search", form=form)


if __name__ == '__main__':
    app.run(debug=True)
