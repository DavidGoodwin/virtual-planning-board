/**
 * @copyright Pale Purple Ltd - http://www.palepurple.co.uk/ - &copy; 2006 onwards.
 * @licence GPL v2 or later - as specified in the LICENCE.txt file in the root of this project.
 */

window.addEvent('domready', function() {
    dropMenu = new PP_DropMenu();
});

function PP_DropMenu(){
    this.dropmenus = $$('.pp_dropmenu');
    this.current = null;
    this.over = false;
    this.init();
}

/**
 * Set everything up
 */
PP_DropMenu.prototype.init = function(){
   this.hideMenus();
   this.makeHeaderLinks(); 
}

PP_DropMenu.prototype.makeHeaderLinks = function() {
    this.dropmenus.each(function(dropmenu) {
        header = dropmenu.getFirst();

        if(header == null){
            console.log("error with formatting...exiting");
            return;
        }

        header_text = header.getText();

        header_link = new Element('a');
        header_link.addClass('header_title');
        header_link.setProperty('href', '#');
        header_link.setText(header_text);

        header.empty();
        header_link.injectInside(header);

        header_link.addEvent('click', this.showMenu.bind(this));
    }, this);
}

PP_DropMenu.prototype.hideMenus = function() {
    this.dropmenus.each(function(dropmenu) {
        actual = dropmenu.getElement("ul");
        actual.setStyle("display", "none");
    });
}

PP_DropMenu.prototype.hideCurrentMenu = function() {
    if(this.current == null) return;

    this.current.removeEvents();
    this.current.setStyle("display", "none");
}

PP_DropMenu.prototype.showMenu = function(e) {
    e = new Event(e);
    e.stop();

    this.hideMenus();

    target_a = e.target;
    target_menu = target_a.getParent().getParent();
    actual = target_menu.getElement("ul");
    this.current = actual;
    actual.setStyle("display", "block");
    actual.addEvent('mouseenter', this.enterMenu.bind(this));

    (function() {
        if(!this.over){
            this.hideCurrentMenu();
        }
     }).delay(2000, this);

}

PP_DropMenu.prototype.enterMenu = function(e) {
    e = new Event(e);
    actual = e.target;
    this.over = true;
    this.current.addEvent('mouseleave', this.exitMenu.bind(this));
}

PP_DropMenu.prototype.exitMenu = function(e) {
    this.over = false;
    this.hideCurrentMenu();
}
