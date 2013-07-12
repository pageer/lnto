PageHeader = {
	handlers: {
		bookmarklet_expand: function () {
			var $this = $(this);
			if ($this.hasClass('expanded')) {
				$this.text('(+)');
				$this.removeClass('expanded');
				$this.next().remove();
			} else {
				$this.addClass('expanded');
				$this.text('(-)');
				var $input = $('<input type="text" class="bookmarklet-text" />');
				$input.val($this.closest('.bookmarklet').find('.link').attr('href'));
				$this.after($input);
				$input.select();
			}
		},
		notification_flash: function() {
			var $notes = $('.notifications');
			var hider = function () {
				$notes.animate({'opacity': 0}, 500, function () { $notes.hide(); });
			};
			$notes.css('opacity', 0);
			$notes.animate({'opacity': 1}, 500, function () {
				setTimeout(hider, 10000);
			});
		}
	},
	init: function () {
		var $bookmarklets = $('#header .bookmarklet'),
		    $node = $('<a href="javascript:void(0)" class="expand" title="Show bookmarklet code">(+)</a>').on('click.pageheader', this.handlers.bookmarklet_expand);
		$bookmarklets.find('.link').after($node);
	
		this.handlers.notification_flash();	
	}
};

Dashboard = {
	handlers: {
		remove_module: function () {
			var $self = $(this),
				link_name = $self.parents('li').find('.name').text(),
				linkid = $self.data('linkid');
			if (!confirm('Delete this module?')) {
				return false;
			}
			var posturl = BASE_URL + 'api/modules/delete';
			$.post(posturl, {moduleid: linkid}, function (data, textStatus, jzXHR) {
				if (data.status == 'success') {
					$self.parents('li').remove();
				} else {
					alert(data.message);
				}
			});
		}
	},
	init: function () {
		//var rem_link = $('<a href="javascript:void(0)">-</a>').on('click.module', this.handlers.remove_module);
		//$('.linkpanel .header').append(rem_link);
	}
};

LinkEditor = {
	handlers: {
		delete_link: function (e) {
			$('.link-list .menulink').removeClass('showit');
			var $self = $(this),
				link_name = $self.parents('li').find('.name').text(),
				linkid = $self.data('linkid');
			if (!confirm('Delete "'+link_name+'"?')) {
				return false;
			}
			var posturl = BASE_URL + 'api/links/delete';
			$.post(posturl, {linkid: linkid}, function (data, textStatus, jzXHR) {
				if (data.status == 'success') {
					$self.parents('li').remove();
				} else {
					alert(data.message);
				}
			});
			$('.link-list .menulink').removeClass('showit')
			return false;
		},
		menu_on: function (e) {
			$('.link-list .menulink').removeClass('showit');
			$(this).toggleClass('showit');
			e.stopPropagation();
		},
		menu_off: function () {
			$('.link-list .menulink').removeClass('showit');
		}
	},
	init: function() {
		$('.link-list .button.delete').on('click.linkeditor', this.handlers.delete_link);
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