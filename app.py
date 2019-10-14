from flask import Flask, render_template, flash
from forms import SearchForm
import numpy
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'u7PrtQm5Dur0cgkcyOlOmU7kYm9xy4ng'
champions = {}
bucket = []

# Creating the JSON
with open('ChampionDataset.json') as json_file:
    champions = json.load(json_file)

# Creating a bucket of words
for champion in champions:
    # text = champion["Name"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"]
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
    bucketLength = len(bucket)
    championsSorted = champions[:]  # Copy without reference
    topFive = []                    # Used as the return variable

    for championIndex in range(len(championsSorted)):
        wordDataArray = []          # Number of documents the term appears in
        score = 0                   # Total score per document

        for termIndex in range(len(searchInputs)):

            # Calculates the number of documents that contain the term
            docTermFrequency = getTermCount(searchInputs[termIndex])

            #Calculate TF for term
            tf = bucket[championIndex].count(searchInputs[termIndex].upper()) / len(bucket[championIndex])

            # Calculate IDF for term
            if docTermFrequency == 0:
                idf = 0
            else:
                idf = numpy.log(bucketLength / docTermFrequency)

            # Calculate TF-IDF total
            score = score + (tf * idf)

            # Creating word data for array
            wordData = {
                "Term": searchInputs[termIndex],
                "Frequency": docTermFrequency,
                "Tf": tf,
                "Idf": idf,
                "Index": championIndex
            }
            wordDataArray.append(wordData)

        championsSorted[championIndex]["WordData"] = wordDataArray
        championsSorted[championIndex]["Score"] = score

    # Sorting the list so the highest scores are first
    championsSorted.sort(key=lambda x: x['Score'], reverse=True)

    # Grabbing top 5 results
    for i in range(0, 5):
        topFive.append(championsSorted[i])

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
