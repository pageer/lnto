/*
 * Viewport - jQuery selectors for finding elements in viewport
 *
 * Copyright (c) 2008-2009 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Project home:
 *  http://www.appelsiini.net/projects/viewport
 *
 */
// Minified version of this file copied inline to save the extra request.
(function($){$.belowthefold=function(element,settings){var fold=$(window).height()+$(window).scrollTop();return fold<=$(element).offset().top-settings.threshold;};$.abovethetop=function(element,settings){var top=$(window).scrollTop();return top>=$(element).offset().top+$(element).height()-settings.threshold;};$.rightofscreen=function(element,settings){var fold=$(window).width()+$(window).scrollLeft();return fold<=$(element).offset().left-settings.threshold;};$.leftofscreen=function(element,settings){var left=$(window).scrollLeft();return left>=$(element).offset().left+$(element).width()-settings.threshold;};$.inviewport=function(element,settings){return!$.rightofscreen(element,settings)&&!$.leftofscreen(element,settings)&&!$.belowthefold(element,settings)&&!$.abovethetop(element,settings);};$.extend($.expr[':'],{"below-the-fold":function(a,i,m){return $.belowthefold(a,{threshold:0});},"above-the-top":function(a,i,m){return $.abovethetop(a,{threshold:0});},"left-of-screen":function(a,i,m){return $.leftofscreen(a,{threshold:0});},"right-of-screen":function(a,i,m){return $.rightofscreen(a,{threshold:0});},"in-viewport":function(a,i,m){return $.inviewport(a,{threshold:0});}});})(jQuery);

/*
 * Main lnto JS begins.
 */
Menu = {
	adjust_position: function ($elem) {
		var win_width = $(window).outerWidth(),
		    width = $elem.outerWidth(),
			pos = $elem.offset(),
			adjustment = win_width - (pos.left + width + 5);
		if (adjustment < 0) {
			$elem.css('left', adjustment);
		} else if (Math.floor(adjustment) == parseInt($elem.css('left'), 10)) {
			$elem.css('left', 'auto');
		}
	}
};
PageHeader = {
	handlers: {
		bookmarklet_expand: function () {
			var $this = $(this);
			if ($this.hasClass('expanded')) {
				$this.text('[+]');
				$this.removeClass('expanded');
				$this.next().remove();
			} else {
				$this.addClass('expanded');
				$this.text('[-]');
				var $input = $('<textarea class="bookmarklet-text" readonly></textarea>'),
				    $panel = $('<div class="bookmarklet-panel"></div>').append($input);
				$input.val($this.closest('.bookmarklet').find('.jslink').attr('href'));
				$this.after($panel);
				$input.select();
			}
		},
		menu_toggle: function (e) {
			var $item = $(this).closest('.submenu-item');
			$item.toggleClass('showit');
			Menu.adjust_position($item.find('.submenu'));
			e.stopPropagation();
		},
		notification_flash: function() {
			var $notes = $('.notifications'),
			    timerid = 0;
			var hider = function () {
				$notes.animate({'opacity': 0}, 500, function () { $notes.hide(); });
			};
			$notes.css('opacity', 0);
			$notes.animate({'opacity': 1}, 500, function () {
				timerid = setTimeout(hider, 5000);
			});
		}
	},
	init: function () {
		var $bookmarklets = $('#header .bookmarklet'),
		    $node = $('<a href="javascript:void(0)" class="link expand" title="Show bookmarklet code">[+]</a>').on('click.pageheader', this.handlers.bookmarklet_expand);
		$bookmarklets.find('.jslink').after($node);
		$('#header .menu-toggle').on('click.pageheader', this.handlers.menu_toggle);
		$('#header .submenu').on('click.pageheader', function(e) {
			e.stopPropagation();
		});
	
		this.handlers.notification_flash();	
	}
};

Dashboard = {
	handlers: {
		create_menu: function () {
			var $menu_link = $('<a class="mod-config-link menu-icon inline" href="javascript:void(0)"></a>'),
				$menu = $('<div class="menu"></div>'),
				$remove_link = $('<a class="button" href="javascript:void(0)">Remove</a>'),
				$config_link = $('<a class="button config" href="javascript:void(0)">Configure</a>');
			$menu_link.on('click.modconfig', this.show_menu);
			$remove_link.on('click.modconfig', this.remove_module);
			$config_link.on('click.modconfig', this.configure_module);
			$menu.append($remove_link);
			$menu.append($config_link);
			$menu_link.append($menu);
			return $menu_link;
		},
		show_menu: function (e) {
			LinkEditor.handlers.menu_off();
			var $this = $(this);
			$this.toggleClass('showit');
			Menu.adjust_position($this.find('.menu'));
			e.stopPropagation();
		},
		create_arrow: function (direction) {
			var $arrow = $('<a href="javascript:void(0)" class="move-'+direction+'"></a>');
			$arrow.on('click.movemod', direction == 'up' ? this.move_up : this.move_down);
			return $arrow;
		},
		move_up: function () {
			$mod = $(this).closest('.module');
			$mod.prev().before($mod);
			$('#sort-form').submit();
		},
		move_down: function () {
			$mod = $(this).closest('.module');
			$mod.next().after($mod);
			$('#sort-form').submit();
		},
		remove_module: function () {
			var $self = $(this),
			    modid = $self.closest('.linkpanel').data('moduleid');
			if (!confirm('Delete this module?')) {
				return false;
			}
			var posturl = BASE_URL + 'api/modules/delete';
			$.post(posturl, {moduleid: modid}, function (data, textStatus) {
				if (data.status == 'success') {
					$self.closest('.linkpanel').remove();
					LinkEditor.handlers.menu_off();
				} else {
					alert(data.message);
				}
			});
			return true;
		},
		configure_module: function () {
			var $mod = $(this).closest('.linkpanel');
			window.location = BASE_URL + 'modules/config/' + $mod.data('moduleid');
		},
		last_module: function () {
			var $first_visible = $('.linkpanel:in-viewport:first'),
				$first_header = $first_visible.find('.header'),
				$prev = $first_visible.prev();
			if ($first_header.is(':in-viewport') && $prev.length > 0) {
				$(document).scrollTop($prev.offset().top);
			} else {
				$(document).scrollTop($first_visible.offset().top);
			}
		},
		next_module: function () {
			var $last_visible = $('.linkpanel:in-viewport:last'),
			    next_pos = $last_visible.next().offset().top;
			$(document).scrollTop(next_pos);
		}
	},
	init: function () {
		var $mods = $('.module-config-sort .module');
		$mods.prepend(this.handlers.create_arrow('down'));
		$mods.prepend(this.handlers.create_arrow('up'));
		$('#sort-form').ajaxForm();
		$('.linkpanel .header').append(this.handlers.create_menu());
		
		if ($('.linkpanel').length > 0) {
			var $last_arrow = $('<a class="mod-nav last" href="javascript:void(0)">&lt;-&nbsp;Last</a>'),
			    $next_arrow = $('<a class="mod-nav next" href="javascript:void(0)">Next&nbsp;-&gt;</a>');
			$last_arrow.on('click.dashboard', this.handlers.last_module);
			$next_arrow.on('click.dashboard', this.handlers.next_module);
			$('#content').append($last_arrow).append($next_arrow);
		}
	}
};

LinkEditor = {
	handlers: {
		delete_link: function (e) {
			$('.link-list .menulink').removeClass('showit');
			var $self = $(this),
				link_name = $self.parents('li').find('.name').text(),
				linkid = $self.closest('.menu').data('linkid');
			if (!confirm('Delete "'+link_name+'"?')) {
				return false;
			}
			var posturl = BASE_URL + 'api/links/delete';
			$.post(posturl, {linkid: linkid}, function (data, textStatus) {
				if (data.status == 'success') {
					$self.parents('li').remove();
				} else {
					alert(data.message);
				}
			});
			LinkEditor.handlers.menu_off();
			return false;
		},
		add_tag: function (e) {
			if (e.keyCode == 13) { //Enter key
				var $self = $(this),
				    linkid = $self.closest('.menu').data('linkid'),
				    tags = $self.val(),
				    posturl = BASE_URL + 'api/links/tag';
				$.post(posturl, {linkid: linkid, tags: tags}, function (data, textStatus) {
					if (data.status == 'success') {
						// And this is where we need an MV* framework....
						$self.val('');
						LinkEditor.handlers.menu_off();
					} else {
						alert(data.message);
					}
				});
			}
		},
		menu_on: function (e) {
			LinkEditor.handlers.menu_off();
			var $this = $(this);
			$this.toggleClass('showit');
			Menu.adjust_position($this.parent().find('.menu'));
			e.stopPropagation();
		},
		menu_off: function () {
			$('.showit').removeClass('showit');
		}
	},
    tags_init: function() {
        var availableTags = $('.tag-select option').map(function (idx, value) {
            var val = $(value).attr('value');
            return val ? val : null;
        });

        $('#tags_string').tagit({
            singleField: true,
            allowSpaces: true,
            availableTags: availableTags,
            placeholderText: 'Comma-separated list of tags',
            showAutocompleteOnFocus: true
        });
        $('.tag-select').hide();
    },
	init: function() {
		$('.link-list .button.delete').on('click.linkeditor', this.handlers.delete_link);
		$('.link-list .box.tag').on('keypress.linkeditor', this.handlers.add_tag);
		$('.link-list .menulink').on('click.linkeditor', this.handlers.menu_on);
        this.tags_init();
		$(document).on('click.linkeditor', this.handlers.menu_off);
	}
};

IndividualEditor = {
	handlers: {
		pick_tag: function () {
			var val = $(this).val(),
				$tags = $('#tags'),
			    curr_tags = $tags.val().split(','),
				prefix = ', ';
			for (var i in curr_tags) {
				if ($.trim(curr_tags[i]) == val) {
					return;
				}
			}
			if ($.trim($tags.val()) == '') {
				prefix = '';
			}
			$tags.val($tags.val() + prefix + val);
		},
		link_modified: function () {
			var posturl = BASE_URL + 'api/links/fetch',
			    url = $(this).val(),
				$form = $('#add-link-form'),
				$spinner = $('<span class="updating"></span>');
			$form.find('#name, #description').after($spinner);
			$.post(posturl, {url: url}, function (response, textStatus) {
				console.log("Response is ", response.status);
				if (response.status != 'success') {
                    $form.find('.updating').remove();
					console.log(response.message);
					return;
				}
				if (response.data.name) {
					$form.find('#name').val(response.data.name);
				}
				if (response.data.description) {
					$form.find('#description').val(response.data.description);
				}
				$form.find('.updating').remove();
			});
		}
	},
	init: function () {
		$('#add-link-form .tag-picker').on('change.editform', this.handlers.pick_tag);
		$('#add-link-form #url').on('change.editform', this.handlers.link_modified);
	}
};

BulkEditor = {
	handlers: {
		toggle_all: function (e) {
			e.preventDefault();
			var $boxes = $('.bulk-select'),
				num_selected = $boxes.filter(':checked').length,
				total_boxes = $boxes.length;
			if (num_selected == total_boxes) {
				$boxes.prop('checked', false);
				$(this).prop('checked', false);
			} else {
				$boxes.prop('checked', true);
				$(this).prop('checked', true);
			}
		},
		change_tag: function () {
			$('.bulk-editor .filter-tag').submit();
		},
		toggle_edit_controls: function () {
			$('.controls, .bulk-select, .js-controls').toggle();
			try {
				if ($('.controls').is(':visible')) {
					localStorage.removeItem('hide_bulk_edit_control');
				} else {
					localStorage.hide_bulk_edit_control = true;
				}
			} catch (e) {
				console.log("Error writing to local storage");
			}
		},
		delete_click: function (e) {
			var num_selected = $('input.bulk-select:checked').length;
			if (num_selected == 0 || !confirm('Really delete all selected links?')) {
				e.preventDefault();
				return false;
			}
			return true;
		}
	},
	init: function() {
		var $toggle_box = $('<a href="javascript:void(0)" id="toggle-check">Toggle all</a>'),
		    $js_controls = $('<div class="js-controls"></div>');
		$js_controls.append($toggle_box);
		$('.bulk-editor .controls').after($js_controls);
		$toggle_box.on('click.bulkeditor', this.handlers.toggle_all);
		$('.bulk-editor li').on('click.bulkeditor', function() {
			var $box = $(this).find('input.bulk-select');
			$box.prop('checked', !$box.is(':checked'));
		});
		$('.bulk-editor li input.bulk-select').on('click.bulkeditor', function(e) {
			e.stopPropagation();
		});
		
		var $delete_selected = $('<input type="submit" name="delete_selected_submit" value="Delete Selected"/>'),
			$delete_panel = $('<div class="edit-panel delete-links"></div>');
		$delete_selected.on('click.bulkeditor', this.handlers.delete_click);
		$delete_panel.append($delete_selected);
		$('.bulk-editor .controls').append($delete_panel);
		
		$('#tag-select').on('change.bulkeditor', this.handlers.change_tag);
		$('.bulk-editor .filter-tag input[type=submit]').hide();
		
		var $show_controls_link = $('<a href="javascript:void(0)" id="toggle-controls">Toggle edit controls</a>');
		$show_controls_link.on('click.bulkeditor', this.handlers.toggle_edit_controls);
		
		try {
			if (localStorage.hide_bulk_edit_control) {
				this.handlers.toggle_edit_controls();
			}
		} catch(e) {
			console.log("Error reading from local storage");
		}
		
		$('.bulk-editor .filter-tag').after($show_controls_link);
	}
};

$(document).ready(function () {
	PageHeader.init();
	Dashboard.init();
	LinkEditor.init();
	IndividualEditor.init();
	BulkEditor.init();
});
