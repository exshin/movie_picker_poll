var margin = {top: 20, right: 20, bottom: 250, left: 40},
    width = 960 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var x0 = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var x1 = d3.scale.ordinal();

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x0)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var yAxisOptions = ["Rated","Years","Rating","Genre"];
var current_selection = "Rated";
var groupOptions = ["Your_Votes","Average_Votes"];
var current_group = "Your_Votes";
var file_name = "/static/data/"+current_selection+".csv";

var color = d3.scale.ordinal()
    .range(["rgba(11,94,215,.8)", "rgba(245, 143, 8, 0.8)"]);

var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) {
      return "<strong>Votes:</strong> <span style='color:red'>" + d.value + "</span>";
    });

var svg = d3.select("#barchart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.call(tip);

d3.csv(file_name, function(error, data) {

  var voteNames = d3.keys(data[0]).filter(function(key) { return key !== "Category"; });

  data.forEach(function(d) {
    d.votes = voteNames.map(function(name) { return {name: name, value: +d[name]}; });
  });

  x0.domain(data.map(function(d) { return d.Category; }));
  x1.domain(voteNames).rangeRoundBands([0, x0.rangeBand()]);
  y.domain([0.0, d3.max(data, function(d) { return d3.max(d.votes, function(d) { return d.value; }); })]);
  
  //x-axis
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .selectAll("text")
     .style("text-anchor", "end")
     .attr("dx", "-.8em")
     .attr("dy", ".15em")
     .attr("transform", function(d) {
         return "rotate(-65)" 
     });

  //y-axis
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Number of Votes");


  var category = svg.selectAll(".category")
      .data(data)
    .enter().append("g")
      .attr("class", "bar")
      .attr("transform", function(d) { return "translate(" + x0(d.Category) + ",0)"; });

  var bars = category.selectAll("rect")
      .data(function(d) { return d.votes; })
    .enter().append("rect")
      .attr("class", "rect")
      .attr("width", x1.rangeBand())
      .attr("x", function(d) { return x1(d.name); })
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); })
      .style("fill", function(d) { return color(d.name); })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);


  // Build Legend
  var legend = svg.selectAll(".legend")
      .data(voteNames.slice().reverse())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d; });

	// Build menus
	d3.select('#y-axis-menu-bar')
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
			svg.selectAll("rect").data([]).exit().remove();
			file_name = "/static/data/" + d + ".csv";
			updateChart(file_name);
			updateMenus();
			legend.append("rect")
		      .attr("x", width - 18)
		      .attr("width", 18)
		      .attr("height", 18)
		      .style("fill", color);
		});

	function updateMenus() {
		d3.select('#y-axis-menu-bar')
		  .selectAll('button')
		  .classed('btn-primary', function(d) {
			return d === current_selection;
		})
		d3.select('#group-menu')
		  .selectAll('li')
		  .classed('selected', function(d) {
			return d === current_group;
		})
	  };

	function updateChart(file_name) {

		var data_new = [];
		d3.csv(file_name, function(error, data) {
			var voteNames = d3.keys(data[0]).filter(function(key) { return key !== "Category"; });
			data.forEach(function(d) {
			    d.votes = voteNames.map(function(name) { return {name: name, value: +d[name]}; })
			    data_new.push(voteNames.map(function(name) { return {name: name, value: +d[name]}; }));
		});

		console.log(data)
		console.log(data_new)

		x0.domain(data.map(function(d) { return d.Category; }));
		x1.domain(voteNames).rangeRoundBands([0, x0.rangeBand()]);
		y.domain([0.0, d3.max(data, function(d) { return d3.max(d.votes, function(d) { return d.value; }); })]);

		//Update x-axis
		svg.select(".x.axis")
			.transition()
			.duration(500)
			.call(xAxis)
			.selectAll("text")
	     .style("text-anchor", "end")
	     .attr("dx", "-.8em")
	     .attr("dy", ".15em")
	     .attr("transform", function(d) { return "rotate(-65)" });
			
		//Update y-axis
		svg.select(".y.axis")
			.transition()
			.duration(500)
			.call(yAxis);

		 //filling chart with data (multiple)    
	    var category_remove = svg.selectAll(".category")
	      	.data(data)
	    	.exit().remove();

	    category_remove.selectAll("rect")
	     	.data(function(d) { return d.votes; })
	     	.exit().remove();

		 //filling chart with data (multiple)    
	    var category = svg.selectAll(".category")
	      .data(data)
	    .enter().append("g")
	      .attr("class", "g")
	      .attr("transform", function(d) { return "translate(" + x0(d.Category) + ",0)"; });

	    category.selectAll("rect")
	      .data(function(d) { return d.votes; })
	    .enter().append("rect")
	      .attr("x", function(d) { return x1(d.name); })
	      .attr("width", x1.rangeBand())
	      .attr("y", function(d) { return y(d.value); })
	      .attr("height", function(d) { return height - y(d.value); })
	      .style("fill", function(d) { return color(d.name); })
	      .on('mouseover', tip.show)
	      .on('mouseout', tip.hide);


		  });
		}
	});
