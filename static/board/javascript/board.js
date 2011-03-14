/*
 * @copyright Pale Purple Ltd - http://www.palepurple.co.uk/ - &copy; 2006 onwards.
 * @licence GPL v2 or later - as specified in the LICENCE.txt file in the root of this project.
 */

/**
 * Virtual Planning Board
 * Author: Ade @ Pale Purple
 * TODO:
 *      -> far too long so needs to be chopped up more
 *      -> more commenting
 * DONE -> use namespaces 
 */

function PP_Util(){
    var locked = false;

    this.getLocked = function() {
        return locked;
    }

    this.toggleLock = function() {
        if(locked){
            locked = false;
            $('lock').setStyle('display', 'none');
            $('lock_open').setStyle('display', 'block');
        }else{
            locked = true;
            $('lock').setStyle('display', 'block');
            $('lock_open').setStyle('display', 'none');
        }
    }
}

var PP_Ticket = new Class({
    initialize: function(ticket) {
        //private variable
        var ticket = ticket;

        //privileged function within constructor
        this.getTicket = function() {
            return ticket;
        }

    },
    getDropper: function(){
        if(this.getTicket() != null){
            return this.getTicket().getParent();
        }
        
        return null;
    },
    getWeek: function(){
        if(this.getDropper() != null){
            return this.getDropper().getParent();
        }

        return null;
    }
});

var pp_util = new PP_Util();

window.addEvent('domready', function() {
    var board = new PP_Board();
    board.init();

    window.addEvent('resize', function() {
        if(board.ticket_change){
            //console.log("Window has been resized, therefore saving all changes made since last save");
            board.saveChanges();
        }
        board.closeTicketBar();    
    });
});

function PP_Board() {
    this.number_of_droppers = 0;
    this.weeks_changed = [];
    this.page = 1;
    this.pages = 1;
    this.ticket_change = false;
    this.ticket_count = 0;
    this.ticket_total = 0;
    // XXX Change this to your URL... 
    this.trac_url = "https://trac.palepurple.co.uk/projects/";
    this.periodical;
    this.saveNotifier;
    this.getting_tickets = false;
    this.ticket_bar_open = false;
    this.active_dropper = null;
    this.saving_disp = null
    this.legend_open = false;
}

PP_Board.prototype.init = function() {
    this.saveNotifier = new SaveNotifier();

    //used for generating new droppers
    //lets us know next id
    this.number_of_droppers = $$('.dropper').length + 1;

    //adds drop on the droppable arears or droppers
	this.addDropEvents();
    //adds dragging on tickets amongst other stuff
    this.addTicketDrag();
    //adds drop on the start dates for appending to the end of the week
    this.addDropStartDates();

    $('lock').setStyle("display", "none");

	$('save-link').addEvent('click', function(e){
            this.saveChanges();
            var e = new Event(e);
            e.stop();
	    }.bind(this)
    );
	
    $('hide-link').addEvent('click', function(e){
            this.toggleTicketBar();
            var e = new Event(e);
            e.stop();
	    }.bind(this)
    );

    $('legend').addEvent('click', function(e){
            this.toggleLegend();
            var e = new Event(e);
            e.stop();
        }.bind(this)
    );

    $('clear-search').addEvent('click', function(e){
            if(this.ticket_change) return;

            $('s_project_id').value = "";
            $('s_ticket_title').value = "";
            $('s_trac_id').value = "";
            this.getUnassignedTickets(this.page);
            var e = new Event(e).stop();
        }.bind(this)
    );

    $('search-button').addEvent('click', function(e) {
            if(!this.ticket_change){
                this.page = 1;
                $('page').setText(this.page);
                this.getUnassignedTickets(this.page);
            }else{
                if($('error').getText() == ""){
                    //var el = $('error');
                    //el.setText("Can't search before changes have been saved");
                }
            }

            if(e != null) var e = new Event(e).stop();
        }.bind(this)
    );
    
    this.checkArrows();
    this.setUpArrows();

    //add key press events
    document.onkeydown = function(event) {
        var event = new Event(event);

        //console.log(event.code);

        //Enter button for searching tickets when ticket bar is open
        if(event.code == 13 && this.ticket_bar_open){ 
            $('search-button').fireEvent('click'); 
        }
        //toggle ticket bar - t
        else if(event.code == 84){
            this.toggleTicketBar();
        }
        //toggle ticket bar - l
        else if(event.code == 76){
            this.toggleLegend();
        }
        //Escape button when viewing ticket details
        else if(event.code == 27){
            if($('lrg-ticket')){
                this.lrgTicket.remove();
                pp_util.toggleLock();
                this.active_dropper.removeClass("dropper-selected");
            }
        }
        
    }.bind(this)

    var myTips = new Tips($$('.ticket-title'), {
        fixed: true,    
    });
}


/**
 * Makes week start dates 'droppable'
 */
PP_Board.prototype.addDropStartDates = function(){

    $$('.start-date').each(function(drop, index){

        drop.addEvents({
            'over':function(el, obj){
                if(!this.canDrop(el)) return;

                var my_non_bleh_id = el.id.substring(0, el.id.lastIndexOf("-"));
				var the_ticket = $(my_non_bleh_id);

                var week_id = "week" + drop.id.substring(drop.id.indexOf("-"), drop.id.length);
    			var their_week = $(week_id);

                var ticket = new PP_Ticket(the_ticket);

                //where am I from and who's my parent
			    var my_id = the_ticket.id;
			    var my_week = ticket.getWeek();
			    var my_ticket = $(my_id);

                //this functionality is only allowed when moving to a different week
			    if((their_week != my_week) && (their_week.id != 'week-homeless')){
                    
                    drop.addClass("start-date-over");

	                var their_last_dropper = their_week.getLast();
                    var new_week = true;
                    this.addPriorityInfo(el, their_last_dropper, new_week);
                }
            }.bind(this),
            'leave': function(el, obj){
                drop.removeClass("start-date-over");
                this.clearPriorityInfo();
            }.bind(this),
            'drop': function(el, obj){
                if(!this.canDrop(el)){
                    el.remove();
                    return;
                }
                drop.removeClass("start-date-over");

                this.clearPriorityInfo();

                var my_non_bleh_id = el.id.substring(0, el.id.lastIndexOf("-"));
                var the_ticket = $(my_non_bleh_id);
				this.addToEnd(the_ticket, drop);
                el.remove();
            }.bind(this)
        });
    }, this);
}

/**
 * Adds a ticket to the end of a week
 */
PP_Board.prototype.addToEnd = function(the_ticket, drop){
    //get week to put it in
    var week_id = "week" + drop.id.substring(drop.id.indexOf("-"), drop.id.length);
    var their_week = $(week_id);

    var ticket = new PP_Ticket(the_ticket);

    //where am I from and who's my parent
    var my_id = the_ticket.id
    var my_parent = ticket.getDropper();
    var my_week = ticket.getWeek();
    var my_ticket = $(my_id);

    //not allowed for same week or for homeless week
	if((their_week == my_week) || (their_week.id == 'week-homeless')){
        return;
    }

	//find out how many droppers the last column has
	var their_droppers = their_week.getChildren();

    //find dropper to put it into, basically last dropper
	var insert_into_dropper = null;

	for(var i = 0; i < their_droppers.length; i++){
        if(their_droppers[i].getFirst() == null){
            insert_into_dropper = their_droppers[i];
        }
    }

    //if theres no spare dropper, make one
    if(insert_into_dropper == null){
		//if column has room for another dropper, put it in there
        var new_dropper = this.create_new_dropper();
        new_dropper.injectInside(their_week);

        insert_into_dropper = new_dropper;
    }

	my_ticket.injectInside(document.body);

	if(this.isWeek(my_week)){
        my_parent.empty();
	    this.shiftLeft(my_parent);
        this.removeLastDropperFromWeek(my_week);
        this.repopulateWeek(my_week);
    }else{
        this.ticket_change = true;
        my_parent.remove();
    }

    my_ticket.injectInside(insert_into_dropper);

	this.addDropEvents();

    this.updateWeek(my_week);
    this.updateWeek(their_week);
}

/**
 * Does the important stuff
 */
PP_Board.prototype.dropFunc = function(drop, el){

    //where am I from and who's my parent
    var my_id = el.id.substring(0, el.id.lastIndexOf("-"));
    var my_parent = $(my_id).getParent();
    var my_week = my_parent.getParent();
    var my_ticket = $(my_id);

    //whos in it?
    var their_parent = drop;
    var their_ticket = their_parent.getFirst();

    //get the destination week
    var their_week = their_parent.getParent();

    //not allowed to add to homeless week
	if(their_week.id == 'week-homeless'){
    	el.remove();
        return;
    }

    //ensure they're trying to drop it into a proper week
    if(!this.isWeek(their_week)){
        el.remove();
        return;
    }

    //don't let it drop to itself
	if(my_parent == their_parent){
        el.remove();
        return;
    }

    //if tickets are indentical return
    if(my_ticket == their_ticket){
        el.remove();
        return;
    }

    //Dropper without a ticket
    if(their_ticket == null){

        //put the ticket somewhere temporarily
		my_ticket.injectInside(document.body);
        //Check 'my week' is a week
        if(this.isWeek(my_week)){
            my_parent.empty();
            this.shiftLeft(my_parent);

            this.removeLastDropperFromWeek(my_week);
		    this.repopulateWeek(my_week);
        }
        else{
            this.ticket_change = true;
            my_parent.remove();
        }

        my_ticket.injectInside(drop);

        this.addDropEvents();

        this.updateWeek(my_week);
        this.updateWeek(their_week);

        el.remove();

        return;
    }

    //Same Week 
    if(my_week == their_week){
        //console.log("same week");

        my_ticket.injectInside(document.body);
		my_parent.empty();

		this.shiftLeft(my_parent);

        //get last dropper of their week
		var last_dropper = their_week.getLast();

        //need to get last ticket of the week
		var last_ticket = last_dropper.getFirst();
        //Shift Right starts at last ticket and finishes at tickets target
        this.shiftRight(last_ticket, last_dropper, their_parent, my_ticket);

        //return new priorities
        //console.log("show new priorities for just my week");
        this.updateWeek(my_week);
    }
    //Different Week
    else {

        var new_dropper = this.create_new_dropper();
        new_dropper.injectInside(their_week);

		my_ticket.injectInside(document.body);
        if(this.isWeek(my_week)){
            my_parent.empty();
            this.shiftLeft(my_parent);

            this.removeLastDropperFromWeek(my_week);
		    this.repopulateWeek(my_week);
        }else{
            this.ticket_change = true;
            my_parent.remove();
        }


        //last dropper of their week
		var last_dropper = their_week.getLast();
        //need to get last ticket of their week
		var last_ticket = last_dropper.getFirst();
        //Shift Right starts at last ticket and finishes at target ticket
		this.shiftRight(last_ticket, last_dropper, their_parent, my_ticket);

        this.addDropEvents();

        this.updateWeek(my_week);
        this.updateWeek(their_week);
    }

    //get rid of the ghost element
    el.remove();
}

/**
 * Adds drag and double click functionality to tickets
 */
PP_Board.prototype.addTicketDrag = function(){

    $$('.ticket').removeEvents();
    $$('.ticket').each(function(item){

        item.getElement(".ticket-title").addEvents({
        	'click': function(e) {

                if(pp_util.getLocked()) return;

                var loading = new Element("div").setProperty("id", "ticket-loading-2");
                var topdist = ((Window.getHeight() / 2) - (100 / 2)) + Window.getScrollTop();
                var leftdist = (Window.getWidth() / 2) - (100 / 2);
                loading.setStyles({"width": "100px", "height": "100px", "z-index": "98", "top":topdist, "left":leftdist, "position":"absolute"});
                loading.injectInside(document.body);

                var dropper = item.getParent();
                dropper.addClass("dropper-selected");

                pp_util.toggleLock();

	            var e = new Event(e).stop();

	            var week = item.getParent().getParent();
	            var week_id = week.id.substring(week.id.indexOf("-") + 1, week.id.length);
	            var priority = this.getDropperPriority(item.getParent());
	            var trac_id = item.getLast().getText();
                var trac_id = trac_id.substring(1, trac_id.length);
                var ticket_id = item.id.substring(item.id.lastIndexOf("-") + 1, item.id.length);

                //get ticket info
                var ticket_url = BASE_URL + 'ticket-info/' + ticket_id + '/';

                var my_ticket = {
                    title:'',
                    desc:'',
                    project:'',
                    owner:'',
                    trac_id: '',    
                    colour: '',
                    est_time: ''
                };                

                var setTicketInfo = function(json) {
                    this.title = json.title;
                    this.desc = json.description; 
                    this.project = json.project;
                    this.owner = json.owner;
                    this.creation_date = json.creation_date;
                    this.trac_id = json.trac_id;
                    this.est_time = json.est_time;
                    this.week = week;
                    this.week_id = week_id;
                    if(json.est_time != null){
                        this.est_time += " hrs";
                    }
                }
                
                var myBoundFunction = setTicketInfo.bind(my_ticket); 
                
                //asynchronous fool!
                var request = new Json.Remote(ticket_url, {
                        onComplete: function (jsonObj){
                            myBoundFunction(jsonObj);
                            build_ticket_html();
                        }

                }).send();

	            //needs to be retrieved via ajax

                var build_ticket_html = function(){
                    var colour = item.getElement('.ticket-title').getStyle('background-color');
                    my_ticket.colour = colour;
                    this.displayTicket(my_ticket, dropper, loading);
                }.bind(this)

            }.bind(this),
            'mouseover': function(e) {
                e = new Event(e);
                var ticket_title = e.target;

                if(ticket_title) {
                    var short_title = ticket_title.getText();
                    var long_title = ticket_title.getElement('span');

                    if(long_title) {
                    }
                }

            }.bind(this),
        });

        item.getElement('div','dragme').addEvents({
			'mousedown': function(e) {

                e = new Event(e).stop();
                
                var dragme = e.target;
                
                if(pp_util.getLocked()) return;

                var my_coords = item.getCoordinates();

                if(item.getParent().getParent().id == 'gallery') {
                   my_coords.top = my_coords.top + window.pageYOffset;
                }

            	var clone = item.clone()
                	.setStyles(my_coords) // this returns an object with left/top/bottom/right, so its perfect
                	.setStyles({'opacity': 0.9, 'position': 'absolute', 'overflow':'visible', 'z-index':32})
                    .setStyles({"width": item.getStyle("width"), "height": item.getStyle("height")})
                	.setProperties({
                    	id: item.id + '-bleh',
                	})
                	.addEvent('emptydrop', function() {
						this.remove();
                	}).inject(document.body);

	            var start_dates = $$('.start-date');
				var droppable_arr = $$('.dropper');

	            var in_count = droppable_arr.length;

				for(var i = 0; i < start_dates.length; i++){
	                droppable_arr[in_count] = start_dates[i];

					in_count++;
				}

	            var drag = clone.makeDraggable({
	                droppables: droppable_arr
	            }); // this returns the dragged element

	            drag.start(e); // start the event manual
        	}.bind(this)
        });

    }, this);
}

/**
 * Updates array that keeps track of the weeks modified since last save in the session
 * Ensures weeks are only added once and that homeless is ignored
 */
PP_Board.prototype.updateWeek = function(week){

    if(week.id == 'week-homeless'){
        return;
    }

    //don't try and push anything that isn't a week
    if(!this.isWeek(week)){
        return;
    }

    for(var i = 0; i < this.weeks_changed.length; i++){
        if(this.weeks_changed[i] == week){
            return;
        }
    }

    this.weeks_changed.push(week);

    this.toggleSaveNotification();
}

function SaveNotifier() {
    this.started = false;
    var effect = $('save-link').effect('background-color', {duration: 800});

    this.fx = function() {
        effect.start('#ffff75').chain(function() {
            effect.start('#ddcbef');
        });
    };
}

SaveNotifier.prototype.startFlashing = function () {
    if(!this.started){
        this.periodical = this.fx.periodical(1700);
        this.started = true;
    }
}

SaveNotifier.prototype.stopFlashing = function () {
    if(this.started){
        $clear(this.periodical);
        this.started = false;
    }
}

PP_Board.prototype.toggleSaveNotification = function() {
    if(this.weeks_changed.length == 0){
        this.saveNotifier.stopFlashing();
    }else{
        this.saveNotifier.startFlashing();
    }
}

/**
 * Saves all the weeks modified since last save
 */
PP_Board.prototype.saveChanges = function(){

    if(pp_util.getLocked()) return;

    if(this.weeks_changed.length > 0){
        $('save-link').setText("...");
        if(this.legend_open) this.toggleLegend();
        pp_util.toggleLock();
        var loading = new Element("div").setProperty("id", "ticket-loading");
        var topdist = 32;
        var leftdist = 0;
        loading.setStyles({"height": "22px", "z-index": "98", "top":topdist, "left":leftdist, "position":"fixed"});
        loading.setStyles({"text-align":"left", "color":"#996AC8"});
        loading.setText("saving ticket changes");
        loading.injectInside(document.body);
        this.saving_disp = loading;
    }

    this.weeks_changed.each(function (week) {

		//get first dropper
    	var first_dropper = week.getFirst();

    	var ticket_arr = [];

    	var current_dropper = first_dropper;

    	var c = 0;

	    while((current_dropper != null) && (current_dropper.getFirst() != null)){

	        var dropper_ticket = current_dropper.getFirst().id;
	        var ticket = dropper_ticket.substring(dropper_ticket.indexOf("-") + 1, dropper_ticket.length);
	        var week_start_date = week.id.substring(week.id.indexOf("-") + 1, week.id.length);
	        var data = {'id': ticket.toInt(), 'week': week_start_date, 'priority': (c + 1)};

	        current_dropper = current_dropper.getNext();

	        ticket_arr[c] = data;
	        c++;
	    }

        this.ticket_total = this.ticket_total + ticket_arr.length;


	    //it might be week now no longer has tickets, in that case don't do anything
	    if(ticket_arr.length > 0){
            var ticket_id = ticket;
	    	this.sendWeek(ticket_arr, ticket_id);
        }

    }, this);
}

/**
 * Each ticket sent through ajax onComplete calls this function
 * When the total number of tickets have been sent, we know we've saved them all!
 */
PP_Board.prototype.ticketSaved = function(){
    this.ticket_count++;

    if(this.ticket_count == this.ticket_total){
        //console.log("saved tickets");
        this.updateWeekInfo();
        this.weeks_changed = [];
        this.toggleSaveNotification();
        this.ticket_change = false;
        pp_util.toggleLock();
        this.page = 1;
        $('page').setText(this.page);
        $('s_project_id').value = "";
        $('s_ticket_title').value = "";
        $('s_trac_id').value = "";
        this.getUnassignedTickets(this.page);
        $('error').setText("");
        $('save-link').setText("Save");
        this.saving_disp.remove();
    }
}

PP_Board.prototype.updateWeekInfo = function() {

    this.weeks_changed.each(function (week) {

        var week_sd = week.id.substring(week.id.indexOf("-") + 1, week.id.length);
        var url = BASE_URL + "week-info/" + week_sd + "/";
		new Ajax(url, {
                        onComplete: function (response){
                            var response = Json.evaluate(response);
                            this.updateWeekInfoDisplay(response);
                        }.bind(this)
		}).request();
    }, this);
}

PP_Board.prototype.updateWeekInfoDisplay = function (json) {

    function hasChanged(element, value) {
        if(element.getText() != value){
            var el_top = element.getCoordinates().top - 20;
            var el_left = element.getCoordinates().left - 5;
            var old_val = element.getText();
            var diff = value - old_val;
            diff = Math.round(diff); 

            diff = diff > 0 ? "+" + diff : diff;
            
            element.setText(value);

            var temp = new Element("span")
                                .setStyles(element.getCoordinates())
                                .setStyle("width", "30px")
                                .setStyle("top", el_top)
                                .setStyle("left", el_left)
                                .setStyle("z-index", 30)
                                .setStyle("position","absolute")
                                .setText(diff)
                                .addClass("week-info-update-tip")
                                .injectInside(document.body);
            
            var fx = temp.effects({duration: 5000, transition: Fx.Transitions.Quart.easeOut});

            fx.start({
                'opacity':1.0
            }).chain(function() {
                this.start.delay(3000, this, {
                    'opacity':0.0
                });
            }).chain(function() {
                temp.remove();
            });
        }
    }


    if(json.success){
        var week = json.week;
        var sd_prefix = "sd-" + week.start_date;

        hasChanged($(sd_prefix + "-week-avail-hours").getElement("span"), week.week_avail_hours);
        hasChanged($(sd_prefix + "-avail-hours-remain").getElement("span"), week.avail_hours_remain);
        hasChanged($(sd_prefix + "-total-est-ticket-times").getElement("span"), week.total_est_ticket_times);
        hasChanged($(sd_prefix + "-total-hours-spent").getElement("span"), week.total_hours_spent);
        hasChanged($(sd_prefix + "-remain-work-hours").getElement("span"), week.remain_work_hours);
        hasChanged($(sd_prefix + "-unassigned-hours").getElement("span"), week.unassigned_hours);
    }

}

/**
 * Sends a weeks' tickets off to the backend
 */
PP_Board.prototype.sendWeek = function(ticket_arr, ticket_id){
    
 	ticket_arr.each(function (ticket) {
        var url = BASE_URL + "save-ticket/" + ticket['id'] + "/" + ticket['priority'] + "/" + ticket['week'] + "/";

		new Ajax(url, {
                        onComplete: function (){
                            this.ticketSaved();    
                        }.bind(this)
		}).request();
 	}, this);
}


/**
 * Grabs all the tickets not assigned to a week
 * and displays them
 */
PP_Board.prototype.getUnassignedTickets = function(page){

    if(this.getting_tickets) return;

    var project = $('s_project_id').value;
    var title = $('s_ticket_title').value;
    var trac_id = $('s_trac_id').value;

    if(project == "") project = 0;
    if(trac_id == "") trac_id = 0;
    if(title == "") title = " "

    this.getting_tickets = true;
    
    var the_page = page - 1;

    //Code to match number of unassigned tickets displayed to screen size 
    var screen_width = Window.getWidth(); 
    var ticket_width = 168;
    var tickets_to_show = Math.floor(screen_width / ticket_width) * 2;

 	var url = BASE_URL + "unassigned-tickets/" + project + "/" + title + "/" + trac_id + "/" + the_page + "/" + tickets_to_show + "/";
    var gallery = $('gallery');
    gallery.addClass('gallery-loading');
    gallery.empty();

    var addTickets = function(tickets) {
        gallery.removeClass('gallery-loading');

        tickets.each(function(ticket) {
            var holder = new Element('div', {'class':'holder'});
            var el = new Element('div', {'id': 'ticket-' + ticket.id, 'class':'ticket'});
            var dragme = new Element('div', {'class':'dragme'}).injectInside(el);
            var el_title = new Element('div', {'class':'ticket-title'}).setHTML(ticket.title).injectInside(el);
            el_title.setStyle('background-color', '#' + ticket.bgcolor);
            var el_id = new Element('div', {'class':'ticket-id'}).injectInside(el);
            var el_owner = new Element('span').setStyles({'float':'left', 'color':'#333'}).setText(ticket.owner).injectInside(el_id); 
            new Element('span').setText('#' + ticket.trac_id).injectInside(el_id);
            el.inject(holder);
            holder.inject(gallery);
        }, this);

        if(tickets.length == 0){
            var el = new Element('h5');
            el.setText("No Tickets Found");
            el.inject(gallery);
        }

        this.addTicketDrag();
    }.bind(this)

    var request = new Json.Remote(url, {
            onComplete: function(jsonObj) {
                addTickets(jsonObj.tickets);
                this.pages = jsonObj.pages;
                $('total_pages').setHTML(this.pages);
                this.setUpArrows();
                this.checkArrows();
                this.getting_tickets = false;
            }.bind(this)
   }).send();
}

/**
 * Works out if an element is a week
 */
PP_Board.prototype.isWeek = function(week){
   var week_id = week.id.substring(0, week.id.indexOf("-")); 

   if(week_id == "week"){
       return true;
   }

   return false;
}
/**
 * @copyright Pale Purple Ltd - http://www.palepurple.co.uk/ - &copy; 2006 onwards.
 * @licence GPL v2 or later - as specified in the LICENCE.txt file in the root of this project.
 */

/**
 * Virtual Planning Board
 * board-dropper.js
 * Contains all the dropper logic
 *  -> create_new_dropper()
 *  -> shiftRight()
 *  -> shiftLeft()
 *  -> removeLastDropperFromWeek()
 *  -> repopulateWeek()
 *  -> getDropperPriority()
 *  -> addDropEvents()
 */

/**
 * Creates a new dropper with a unique incremented id
 */
PP_Board.prototype.create_new_dropper = function(){

    this.number_of_droppers++;

    var new_dropper = new Element('div', {
        'class': 'dropper',
        'id': 'dropper-' + this.number_of_droppers
    });

    return new_dropper;
}

/**
 * Works out priority of a dropper
 * Will be useful when doing the backend hook up
 */
PP_Board.prototype.getDropperPriority = function(dropper){
    var my_week = dropper.getParent();
    var droppers = my_week.getChildren();

    var priority = 0;

    for(var i = 0; i < droppers.length; i++){
        if(dropper == droppers[i]){
            priority = i;
        }
    }

    return priority + 1;
}

/**
 * Shifts a week left from the current dropper
 * This closes the gap created when moving a ticket out of position
 */
PP_Board.prototype.shiftLeft = function(current_dropper){

    if(current_dropper.getNext() == null){
        return;
    }else{
        //get next dropper
        var next_dropper = current_dropper.getNext();
        //get next droppers ticket
        var next_ticket = next_dropper.getFirst();

        if(next_ticket == null){
            //console.log("ERROR no next ticket");
            return;
        }

        next_ticket.injectInside(current_dropper);

        //recurse
        this.shiftLeft(next_dropper);
    }

}

/**
 * Shifts a weeks tickets right from the target_dropper to create space for a new ticket
 * Inserts the ticket into its right place
 */
PP_Board.prototype.shiftRight = function(last_ticket, last_dropper, target_dropper, ticket_to_insert){

    if(last_dropper == target_dropper){
        ticket_to_insert.injectInside(target_dropper);
        return null;
    }
    else {
        //get prev dropper
        var prev_dropper = last_dropper.getPrevious();
        //get prev droppers ticket
        var prev_ticket = prev_dropper.getFirst();

        if(prev_ticket == null){
           //console.log("ERROR no previous ticket");
           return;
        }

        prev_ticket.injectInside(last_dropper);

        var last_dropper = last_dropper.getPrevious();
        this.shiftRight(last_ticket, last_dropper, target_dropper, ticket_to_insert);
    }

}
/**
 * removes the last dropper from a week
 */
PP_Board.prototype.removeLastDropperFromWeek = function(my_week){
        //get rid of the last dropper now in the week
        var my_last_dropper = my_week.getElements('.dropper').getLast();
        my_last_dropper.remove();
}

/**
 * Adds drop functionality for the droppers
 */
PP_Board.prototype.addDropEvents = function(){

    $$('.dropper').each(function(drop, index){

        drop.removeEvents();

        var fx = new Fx.Styles(drop, {duration:200, wait:false});

        drop.addEvents({
            'over': function(el, obj){
                if(!this.canDrop(el)) return;

                this.addPriorityInfo(el, drop, false);
            }.bind(this),
            'leave': function(el, obj){
                this.clearPriorityInfo();
            }.bind(this),
            'drop': function(el, obj){
                if(!this.canDrop(el)) {
                    el.remove();
                    return;
                }

                this.dropFunc(drop, el);
                this.clearPriorityInfo();
            }.bind(this)
        });

    }, this);

}

/**
 * canDrop
 * Ensures user is unable to drop ticket on tickets that are underneath the ticket bar (providing it's open)
 */
PP_Board.prototype.canDrop = function(el) {

    var el_top = el.getCoordinates().top;

    var win_height = Window.getHeight() + Window.getScrollTop();
    var lower_height = $('lower').getStyle("height").substring(0, 3);

    lower_height = lower_height - 0
    lower_height = lower_height + 20;

    if(this.ticket_bar_open){
       if(el_top >= (win_height-lower_height)){
           return false;
       } 
    }

    return true;
}

/**
 * if the week loses all droppers, ensure it still has one, so tickets can be added into it again if necessary
 */
PP_Board.prototype.repopulateWeek = function(week){
    if(week.getChildren().length == 0 && week.id != "week-homeless"){
        //repopulate week with a dropper
        var new_dropper = this.create_new_dropper();
        new_dropper.injectInside(week);
    }
}

/**
 * @copyright Pale Purple Ltd - http://www.palepurple.co.uk/ - &copy; 2006 onwards.
 * @licence GPL v2 or later - as specified in the LICENCE.txt file in the root of this project.
 */

/**
 * Virtual Planning Board
 * board-ui.js
 * Contains all the specific User Interface stuff
 * excluding drag drop
 */

/**
 * Shows and hides the ticket search bar at the bottom of the screen
 */
PP_Board.prototype.toggleTicketBar = function(){

   if(pp_util.getLocked()) return;

   if(this.ticket_bar_open){ 

       if(this.ticket_change) return;

       this.ticket_bar_open = false;

       $('gallery').setStyle("display", "none");
       $('search').setStyle("display", "none");
       $('lower').setStyle("height", "18px");
       $('hide-link').setHTML("show");
   }
   else{
        this.ticket_bar_open = true;

        this.page = 1;
        $('page').setText(this.page);
        this.getUnassignedTickets(this.page);

       $('gallery').setStyle("display", "block");
       $('search').setStyle("display", "block");
       $('lower').setStyle("height", "160px");
       $('hide-link').setHTML("hide");
   }
}

PP_Board.prototype.closeTicketBar = function() {
   if($('hide-link').getText() == "hide"){ 
       $('gallery').setStyle("display", "none");
       $('search').setStyle("display", "none");
       $('lower').setStyle("height", "18px");
       $('hide-link').setHTML("show");
   }
}

PP_Board.prototype.clearPriorityInfo = function(){
    if($$('.priority-info') != null){
        $$('.priority-info').each(function(item) {
            item.remove();
        });
    }
}

/**
 * Adds priority + week info to the bottom of the ghost ticket
 */
PP_Board.prototype.addPriorityInfo = function(el, drop, new_week){

    this.clearPriorityInfo();

    var priority_info = new Element('div', {
        'class': 'priority-info',
    });

    var my_non_bleh_id = el.id.substring(0, el.id.lastIndexOf("-"));
    var origin_dropper = $(my_non_bleh_id).getParent();
    var my_week = origin_dropper.getParent();
    var their_week = drop.getParent();

    var week_str = "";

    if(my_week != their_week){
        week_str = "Move To Week: " + their_week.id.substring((their_week.id.indexOf("-") + 1), their_week.id.length) + "<br/>";
    }

    var new_priority = this.getDropperPriority(drop);

    if((new_week == true) && (drop.getFirst() != null)){
        new_priority++;
    }

    var old_priority = this.getDropperPriority(origin_dropper);

    if(my_week.id == 'week-homeless' || !this.isWeek(my_week)){
        old_priority = "N\\A";
    }

    priority_info.setHTML(week_str + "New Priority: " + new_priority + "<br/>Old Priority: " + old_priority);

    if(their_week.id == 'week-homeless'){
        priority_info.setText("Can't add to or shift in homeless");
    }

    priority_info.injectInside(el);
}

PP_Board.prototype.checkArrows = function(){

    if(this.page == 1){
        $('left-arrow').addClass("disabled");
    }

    if(this.page == this.pages){
        $('right-arrow').addClass("disabled");
    }
    else {
        $('right-arrow').removeClass("disabled");
    }
}

PP_Board.prototype.setUpArrows = function(){

    $('left-arrow').removeEvents();

    $('left-arrow').addEvent('click', function(e) {
            if(this.ticket_change){
                return;
            }

            if(this.page != 1){
                this.page--;
                this.getUnassignedTickets(this.page);
                $('page').setText(this.page);
            }

            if(this.page < this.pages){
                $('right-arrow').removeClass("disabled");
            }

        }.bind(this)
    );

    $('right-arrow').removeEvents();

    $('right-arrow').addEvent('click', function(e) {
            if(this.ticket_change){
                return;
            }

            if(this.page < this.pages){
                this.page++;
                $('page').setText(this.page);
                this.getUnassignedTickets(this.page);
            }

            if(this.page != 1){
                $('left-arrow').removeClass("disabled");
            }
        }.bind(this)
    );
}
/**
 * @copyright Pale Purple Ltd - http://www.palepurple.co.uk/ - &copy; 2006 onwards.
 * @licence GPL v2 or later - as specified in the LICENCE.txt file in the root of this project.
 */

/**
 * Virtual Planning Board
 * board-legend.js
 * Sets up javascript for showing/hiding the legend
 */

PP_Board.prototype.toggleLegend = function(){

    if(pp_util.getLocked()) return; 

    var legend = $('project_colours');
    var llh = $('legend-link-holder');
    var legend_link = $('legend');

    if(!this.legend_open){
        this.legend_open = true;
        legend.setStyle("height", 50);
        llh.setStyle("margin-top", "5em");
        legend_link.getElement('img').setProperty('src', MEDIA_URL + 'board/images/bullet_arrow_up.png');
    }else{
        this.legend_open = false;
        legend.setStyle("height", 25);
        llh.setStyle("margin-top", "2.5em");
        legend_link.getElement('img').setProperty('src', MEDIA_URL + 'board/images/bullet_arrow_down.png');
    }
}

PP_Board.prototype.displayTicket = function (my_ticket, dropper, loading) {

    loading.remove();

    this.active_dropper = dropper;

    var window_height = Window.getHeight();
    var window_width = Window.getWidth();
    var scroll_height = Window.getScrollHeight();
    var scroll_width = Window.getScrollWidth();

    var ticket_width = 420;
    var ticket_height = 335;

    var week = dropper.getParent();
    var priority = this.getDropperPriority(dropper);

    var week_id;

    if(!this.isWeek(week)){
        week_id = "Unassigned";
        priority = "N/A";
    }else{
        week_id = my_ticket.week_id;
    }

    var project_url = my_ticket.project;
    var new_ticket_html = "";
    var trac = "<strong>Trac Id:</strong> <a href=\""+this.trac_url+project_url+"/ticket/"+my_ticket.trac_id+"\">#"+my_ticket.trac_id+"</a>";
    var project = "<strong>Project:</strong> "+my_ticket.project;
    var owner = "<strong>Owner:</strong> "+my_ticket.owner;
    var week = "<strong>Week:</strong> " + week_id;
    week += " - <strong>Priority:</strong> " + priority;
    var created_on = "<strong>Created On:</strong> "+my_ticket.creation_date;
    var est_time = my_ticket.est_time;
    if(est_time == null) est_time = "Unknown";

    var ticket = new Element("div").setProperty("id", "lrg-ticket");
    this.lrgTicket = ticket;
    
    var close = new Element("span").injectInside(ticket);
    close.setStyles({"float":"right", "padding-left": "5px;"});
    new Element("img").setProperty("src", MEDIA_URL + "board/images/close.gif").setStyle("cursor", "pointer").injectInside(close);

    var ticket_header = new Element("div").setProperty("id", "lrg-ticket-header").injectInside(ticket);
    ticket_header.setStyles({"height":30, "background-color": my_ticket.colour});
    ticket_header.setText(my_ticket.title);

    close.addEvent("click", function() {
            ticket.remove();
            pp_util.toggleLock();
            this.active_dropper.removeClass("dropper-selected");
        }.bind(this)
    );


    var ticket_body = new Element("div").setProperty("id", "lrg-ticket-body").injectInside(ticket);
 
    new Element("div").setProperty("id", "lrg-ticket-desc-header").setText("Description").injectInside(ticket_body);

    var ticket_desc = new Element("div").setProperty("id", "lrg-ticket-desc").injectInside(ticket_body); 

    if(my_ticket.desc != ""){
        ticket_desc.setText(my_ticket.desc);
        var tmpstr = my_ticket.desc;
        tmpstr = tmpstr.replace(/\n/g, "<br />");
        ticket_desc.setHTML(tmpstr);
    }else{
        ticket_desc.setText("Empty");
    }

    var ticket_inf = new Element("div").setProperty("id", "lrg-ticket-info").injectInside(ticket_body);
    new Element("div").addClass("lrg-ticket-info-section").setHTML(trac).injectInside(ticket_inf);
    new Element("div").addClass("lrg-ticket-info-section").setHTML(project).injectInside(ticket_inf);
    new Element("div").addClass("lrg-ticket-info-section").setHTML(owner).injectInside(ticket_inf);
    new Element("div").addClass("lrg-ticket-info-section").setHTML(week).injectInside(ticket_inf);
    new Element("div").addClass("lrg-ticket-info-section").setHTML(created_on).injectInside(ticket_inf);
    new Element("div").addClass("lrg-ticket-info-hours").setHTML(est_time).injectInside(ticket_inf);

    var topdist = ((window_height / 2) - (ticket_height / 2)) + Window.getScrollTop();
    var leftdist = (window_width / 2) - (ticket_width / 2);

    ticket.setStyles({"width": ticket_width+"px", "height": ticket_height+"px", "z-index": "99", "top":topdist, "left":leftdist, "position":"absolute"});
    ticket.injectInside(document.body);
}
