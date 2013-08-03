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
				var $input = $('<textarea class="bookmarklet-text"></textarea>'),
				    $panel = $('<div class="bookmarklet-panel"></div>').append($input);
				$input.val($this.closest('.bookmarklet').find('.link').attr('href'));
				$this.after($panel);
				$input.select();
			}
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
		$bookmarklets.find('.link').after($node);
	
		this.handlers.notification_flash();	
	}
};

Dashboard = {
	handlers: {
		create_menu: function () {
			var $menu_link = $('<a class="mod-config-link" href="javascript:void(0)"></a>'),
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
			$(this).toggleClass('showit');
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
		}
	},
	init: function () {
		var $mods = $('.module-config-sort .module');
		$mods.prepend(this.handlers.create_arrow('down'));
		$mods.prepend(this.handlers.create_arrow('up'));
		$('#sort-form').ajaxForm();
		$('.linkpanel .header').append(this.handlers.create_menu());
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
			$(this).toggleClass('showit');
			e.stopPropagation();
		},
		menu_off: function () {
			$('.showit').removeClass('showit');
		}
	},
	init: function() {
		$('.link-list .button.delete').on('click.linkeditor', this.handlers.delete_link);
		$('.link-list .box.tag').on('keypress.linkeditor', this.handlers.add_tag);
		$('.link-list .menulink').on('click.linkeditor', this.handlers.menu_on);
		$(document).on('click.linkeditor', this.handlers.menu_off)
	}
};

BulkEditor = {
	handlers: {
		toggle_all: function () {
			var $boxes = $('.bulk-select'),
				num_selected = $boxes.filter(':checked').length,
				total_boxes = $boxes.length;
			if (num_selected == total_boxes) {
				$boxes.prop('checked', false);
			} else {
				$boxes.prop('checked', true);
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
					localStorage['hide_bulk_edit_control'] = true;
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
		var $toggle_box = $('<label><input type="checkbox" id="toggle-check"/>Toggle all</label>'),
		    $js_controls = $('<div class="js-controls"></div>');
		$js_controls.append($toggle_box);
		$('.bulk-editor .controls').after($js_controls);
		$toggle_box.on('change.bulkeditor', this.handlers.toggle_all);
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
			if (localStorage['hide_bulk_edit_control']) {
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
	BulkEditor.init();
});