var width = 960,
    height = 500,
    radius = Math.min(width, height) / 2;

var color = d3.scale.category20();

var pie = d3.layout.pie()
    .value(function(d) { return d.Total; })
    .sort(null);

var arc = d3.svg.arc()
    .innerRadius(radius - 100)
    .outerRadius(radius - 20);


var yAxisOptions = ["Rated","Years","Rating","Genre"];
var current_selection = "Rated";
var filename = "/static/data/"+current_selection+"_pie.csv";


var svg = d3.select("#piechart").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

var path = svg.selectAll("path");

d3.csv(filename, type, function(error, data) {
  var categoriesByType = d3.nest()
      .key(function(d) { return d.Type; })
      .entries(data)
      .reverse();

  var label = d3.select("form").selectAll("label")
      .data(categoriesByType)
    .enter().append("label");

  label.append("input")
      .attr("type", "radio")
      .attr("name", "Type")
      .attr("value", function(d) { return d.key; })
      .on("change", change)
    .filter(function(d, i) { return !i; })
      .each(change)
      .property("checked", true);

  label.append("span")
      .text(function(d) { return d.key; });

  function change(Category) {
    var data0 = path.data(),
        data1 = pie(Category.values);

    path = path.data(data1, key);

    path.enter().append("path")
        .each(function(d, i) { this._current = findNeighborArc(i, data0, data1, key) || d; })
        .attr("fill", function(d) { return color(d.data.Category); })
      .append("title")
        .text(function(d) { return d.data.Category; });

    path.exit()
        .datum(function(d, i) { return findNeighborArc(i, data1, data0, key) || d; })
      .transition()
        .duration(750)
        .attrTween("d", arcTween)
        .remove();

    path.transition()
        .duration(750)
        .attrTween("d", arcTween);
  }
});

function key(d) {
  return d.data.Category;
}

function type(d) {
  d.Total = +d.Total;
  return d;
}

function findNeighborArc(i, data0, data1, key) {
  var d;
  return (d = findPreceding(i, data0, data1, key)) ? {startAngle: d.endAngle, endAngle: d.endAngle}
      : (d = findFollowing(i, data0, data1, key)) ? {startAngle: d.startAngle, endAngle: d.startAngle}
      : null;
}

// Find the element in data0 that joins the highest preceding element in data1.
function findPreceding(i, data0, data1, key) {
  var m = data0.length;
  while (--i >= 0) {
    var k = key(data1[i]);
    for (var j = 0; j < m; ++j) {
      if (key(data0[j]) === k) return data0[j];
    }
  }
}

// Find the element in data0 that joins the lowest following element in data1.
function findFollowing(i, data0, data1, key) {
  var n = data1.length, m = data0.length;
  while (++i < n) {
    var k = key(data1[i]);
    for (var j = 0; j < m; ++j) {
      if (key(data0[j]) === k) return data0[j];
    }
  }
}

function arcTween(d) {
  var i = d3.interpolate(this._current, d);
  this._current = i(0);
  return function(t) { return arc(i(t)); };
}



// Build menus
d3.select('#y-axis-menu-pie')
	.selectAll('button')
	.data(yAxisOptions)
	.enter()
	.append('button')
	.text(function(d) {return d;})
	.classed('btn-primary', function(d) {
		return d === current_selection;
	})
	.on('click', function(d) {
		current_selection = d;
		file_name = "/static/data/"+d+"_pie.csv";
		updatepieChart(file_name);
		updatepieMenus();
	});

function updatepieMenus() {
	d3.select('#y-axis-menu-pie')
	  .selectAll('button')
	  .classed('btn-primary', function(d) {
		return d === current_selection;
	})
}; 

function updatepieChart(file_name) {
};