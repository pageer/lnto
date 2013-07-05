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
	LinkEditor.init();
	BulkEditor.init();
});