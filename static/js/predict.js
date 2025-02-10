function showResults(val) {
    res = document.getElementById("result");
    res.innerHTML = '';
    if (val == '') {
        return;
    }
    let list = '';
    fetch('https://api.fda.gov/drug/drugsfda.json?api_key=i9UVpz5x5WJjAI0OD9xU0aLK1hEWjnqHAqdvDnJT&search=products.brand_name:' + val).then(
        function(response) {
            return response.json();
        }).then(function(data) {
        for (i = 0; i < data.length; i++) {
            list += '<li>' + data[i] + '</li>';
        }
        res.innerHTML = '<ul>' + list + '</ul>';
        return true;
    }).catch(function(err) {
        console.warn('Something went wrong.', err);
        return false;
    });
}