from flask import Flask, render_template, flash
from forms import SearchForm
import numpy
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'u7PrtQm5Dur0cgkcyOlOmU7kYm9xy4ng'
champions = {}
bucket = []
tfMatrix = {}
topFiveTf = {}

# Creating the JSON
with open('ChampionDataset.json') as json_file:
    champions = json.load(json_file)

# Creating a bucket of words
for champion in champions:
    bucket.append(champion["Name"])
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Title"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Role"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Region"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Bio"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1].upper()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="Home")


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():

        # Splitting search terms
        searchInputs = form.searchInput._value().split()

        # Calculating top 5
        topFive = create_tf_matrix(searchInputs)
        return render_template('search.html', title="Search", form=form, topFive=topFive)
    else:
        flash(f'{form.searchInput} is not valid', 'error')
        return render_template('search.html', title="Search", form=form)


def create_tf_matrix(searchInputs):
    count = 0
    bucketLength = len(bucket)
    returnJson = []
    topFive = []

    # Creating rank matrix
    for term in searchInputs:
        temp = []
        docTermCount = getTermCount(term)

        for doc in bucket:
            tf = doc.count(term.upper()) / len(doc)

            if docTermCount == 0:
                idf = 0
            else:
                idf = numpy.log(bucketLength / docTermCount)

            tfidf = tf * idf

            tempJSON = {
                "TF": tf,
                "IDF": idf,
                "TFIDF": tfidf
            }

            temp.append(tempJSON)
            count += 1
        returnJson.append(temp)

        # Mapping and sorting ranked matrix
        indexScoreArray = []
        for i in range(bucketLength):
            score = 0
            for j in range(len(returnJson)):
                score += returnJson[j][i]["TFIDF"]

            test = {
                "INDEX": i,
                "SCORE": score
            }

            indexScoreArray.append(test)

        indexScoreArray.sort(key=lambda x: x['SCORE'], reverse=True)

    # Grabbing top 5 results
    for i in range(0, 5):
        topFive.append(champions[indexScoreArray[i]["INDEX"]])
        topFive[i]["Score"] = indexScoreArray[i]["SCORE"]

    print(topFive)
    return topFive


def getTermCount(term):
    result = 0
    for doc in bucket:
        tf = doc.count(term.upper())
        if tf > 0:
            result += 1
    return result


if __name__ == '__main__':
    app.run(debug=True)
