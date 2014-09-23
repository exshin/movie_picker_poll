$( document ).ready(function(){
  $(".container").on('click','.groupsBtn',function(e) {
    console.log(e);
    current_group_id = parseInt(e.currentTarget.attributes.value.value);
    console.log(current_group_id);
    check_array = $.inArray(current_group_id, groups_id_list);
    console.log(check_array);
    var join_logic;
    var check_id = "#checked"+current_group_id;
    var divbutton_id = "#buttondiv"+current_group_id;
    var popup_button_id = "#joinleavebutton"+current_group_id;
    if(check_array > -1) {
      // User wants to leave. 
      console.log("Leave Group")
      join_logic = 'leave'
      // Remove current_group_id from groups_id_list list
      var index = groups_id_list.indexOf(current_group_id);
      if (index > -1) {
          groups_id_list.splice(index, 1);
      };
      // Change popup HTML Button to "JOIN" and Toggle Image
      $(check_id).toggle(this.checked);
      var button_string = "<input type='hidden' name='group_id' id='group_id' value='"+current_group_id+"'></input><button type='button' class='btn btn-primary btn-xs groupsBtn' name='groupsBtn' id='groupsBtn' value='"+current_group_id+"' style='width:100%;'>Join</button>";
      $(divbutton_id).html(button_string);
    }
    else {
      // User wants to join. 
      console.log("Join")
      join_logic = 'join'
      // Add current_group_id to groups_id_list list
      groups_id_list.push(current_group_id);
      // Change popup HTML Button to "LEAVE" and Toggle Image
      $(check_id).toggle(this.checked);
      var button_string = "<input type='hidden' name='group_id' id='group_id' value='"+current_group_id+"'></input><button type='button' class='btn btn-danger btn-xs groupsBtn' name='groupsBtn' id='groupsBtn' value='"+current_group_id+"'style='width:100%;'>Leave</button>";
      $(divbutton_id).html(button_string);
    };
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/groupjoinleave/",
        contentType: "application/json; charset=utf-8",
        data: { group_id: $('input[name="group_id"]').val(),
                group_join_or_leave: join_logic },
        success: function(data) {
            groups_id_list = data.groups_id;
            console.log(groups_id_list);
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