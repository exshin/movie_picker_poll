$( document ).ready(function(){
  $(".container").on('click','.voteBtn',function(e) {
    var current_vote_imdbID = e.currentTarget.previousElementSibling.attributes.value.value
    console.log(current_vote_imdbID);
    var check_array = $.inArray(current_vote_imdbID, my_votes);
    var vote_logic
    var check_id = "#checked"+current_vote_imdbID
    var divbutton_id = "#buttondiv"+current_vote_imdbID
    var popup_button_id = "#popup_button_"+current_vote_imdbID
    if(check_array > -1) {
      // User wants to unvote. 
      console.log("Unvote")
      vote_logic = 'unvote'
      // Remove current_vote_imdbID from my_votes list
      var index = my_votes.indexOf(current_vote_imdbID);
      if (index > -1) {
          my_votes.splice(index, 1);
      };
      // Change popup HTML Button to "VOTE" and Toggle Image
      $(check_id).toggle(this.checked);
      var button_string = "<input type='hidden' name='vote_imdbID' id='vote_imdbID' value='"+current_vote_imdbID+"'></input><button type='button' class='btn btn-primary btn-xs voteBtn' name='voteBtn' id='voteBtn'><i class='fa fa-thumbs-up' style='margin-right: 3px'></i>Vote</button></div>";
      $(divbutton_id).html(button_string);
      var popup_button_content = $(popup_button_id)[0].dataset.content;
      new_content = "<div style='float: left; margin-bottom: 15px; margin-top: 5px' id='buttondiv" + current_vote_imdbID + "'>" + button_string +  "<div style='float: left; width: 180px;'>" + popup_button_content.split("<div style='float: left; width: 180px;'>")[1];
      $(popup_button_id)[0].dataset.content = new_content;
    }
    else {
      // User wants to vote. 
      console.log("Vote")
      vote_logic = 'vote'
      // Add current_vote_imdbID to my_votes list
      my_votes.push(current_vote_imdbID);
      // Change popup HTML Button to "UNVOTE" and Toggle Image
      $(check_id).toggle(this.checked);
      var button_string = "<input type='hidden' name='vote_imdbID' id='vote_imdbID' value='"+current_vote_imdbID+"'></input><button type='button' class='btn btn-danger btn-xs voteBtn' name='voteBtn' id='voteBtn'><i class='fa fa-thumbs-down' style='margin-right: 3px'></i>Unvote</button></div>";
      $(divbutton_id).html(button_string);
      var popup_button_content = $(popup_button_id)[0].dataset.content;
      new_content = "<div style='float: left; margin-bottom: 15px; margin-top: 5px' id='buttondiv" + current_vote_imdbID + "'>" + button_string +  "<div style='float: left; width: 180px;'>" + popup_button_content.split("<div style='float: left; width: 180px;'>")[1];
      $(popup_button_id)[0].dataset.content = new_content;
    };
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/voteclick/",
        contentType: "application/json; charset=utf-8",
        data: { vote_imdbID: $('input[name="vote_imdbID"]').val(),
                vote_logic: vote_logic },
        success: function(data) {
            my_votes = data.votes;
            console.log(my_votes);
        }
    });
  });
});

function sort(sort_type) {
  console.log(sort_type);
  if (sort_type != "title") {
    $('.movie-container').sort(function (a, b) {
      return $(b).find('.wrapper').data(sort_type) - $(a).find('.wrapper').data(sort_type);
    }).each(function (_, container) {
      $(container).parent().append(container);
    });
  }
  else {
    var alphabeticallyOrderedDivs = $('.movie-container').sort(function(a, b) {
        return $(a).find('.wrapper').data(sort_type) > $(b).find('.wrapper').data(sort_type) ? 1 : -1;
    }).each(function (_, container) {
      $(container).parent().append(container);
    });
  };
};

function filter() {
  // filters for checked attributes
  m = $(".movie-container");
  d = document.getElementsByName("check");
  check_array = {};
  check_array['rated'] = [];
  check_array['genre'] = [];
  check_array['vote'] = [];
  check_instance = [];
  // hide all first
  $(".movie-container").hide();

  // Determine which divs have the checked attributes
  // Store those divs references in check_array
  for(var i = 0; i < d.length; i++){
    if(d[i].checked) {
      check_instance = d[i].id.split("_");
      console.log(check_instance[0],check_instance[1]);
      for(var n = 0; n < m.length; n++){

        element = m[n].getElementsByClassName('wrapper')[0].dataset[check_instance[0]]

        if (check_instance[0] == 'rated') {
          if ( element == check_instance[1] ) {
              check_array[check_instance[0]].push(n);
          };
        };

        if (check_instance[0] == 'vote') {
          if ( element == check_instance[1] ) {
              check_array[check_instance[0]].push(n);
          };
        };

        if (check_instance[0] == 'genre') {
          if ( element.indexOf(check_instance[1]) != -1 ) {
              check_array[check_instance[0]].push(n);
          };
        };
        
      };
    };
  };

  // Find the intersection of the checked divs
  var cats = ['rated','vote','genre'];
  checked_cats = [];
   for (var c = 0; c < cats.length; c++) {
    if (check_array[cats[c]].length > 0) {
      checked_cats.push(cats[c])
    };
  };
  if (checked_cats.length > 0) {
    if (checked_cats.length == 1) {
      intersection = check_array[checked_cats[0]];
    };
    if (checked_cats.length == 2) {
      intersection = check_array[checked_cats[0]].filter(function(n) {
        return check_array[checked_cats[1]].indexOf(n) != -1
      });
    };
    if (checked_cats.length == 3) {
      intersection1 = check_array[checked_cats[0]].filter(function(n) {
        return check_array[checked_cats[1]].indexOf(n) != -1
      });
      intersection = intersection1.filter(function(n) {
        return check_array[checked_cats[2]].indexOf(n) != -1
      });
    };
    // Show the intersected checked divs
    for (var n = 0; n < m.length; n++) {
      if (intersection.indexOf(n) != -1) {
        m[n].style.display = "block";
        m[n].getElementsByClassName('wrapper')[0].dataset.show = 1;
        console.log(m[n]);
      };
    };
    // sort by "show" attributed to arrange all shown divs at top and hidden at bottom
    $('.movie-container').sort(function (a, b) {
      return $(b).find('.wrapper').data("show") - $(a).find('.wrapper').data("show");
    }).each(function (_, container) {
      $(container).parent().append(container);
    });
  }
  else {
    // no checks; show all
    $(".movie-container").show();
    m = $(".movie-container");
    for (var n = 0; n < m.length; n++) {
      m[n].getElementsByClassName('wrapper')[0].dataset.show = 0;
    };
  };
};

function filter_all() {
  console.log('reset filters');
  $(".movie-container").show();
  d = document.getElementsByName("check");
  for(var i = 0; i < d.length; i++){
    d[i].checked = false;
  };
  m = $(".movie-container");
  for (var n = 0; n < m.length; n++) {
    m[n].getElementsByClassName('wrapper')[0].dataset.show = 0;
  };
};