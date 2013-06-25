LinkEditor = {
	handlers: {
		delete_link: function () {
			var $self = $(this),
				link_name = $self.parents('li').find('.name').text(),
				linkid = $self.data('linkid');
			if (!confirm('Delete "'+link_name+'"?')) {
				return false;
			}
			//var posturl = $self.attr('href');
			var posturl = '/api/links/delete';
			$.post(posturl, {linkid: linkid}, function (data, textStatus, jzXHR) {
				if (data.status == 'success') {
					$self.parents('li').remove();
				} else {
					alert(data.message);
				}
			});
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
			console.log('Toggle that shit');
			var $boxes = $('.bulk-select'),
				num_selected = $boxes.filter(':checked').length,
				total_boxes = $boxes.length;
			if (num_selected == total_boxes) {
				$boxes.prop('checked', false);
			} else {
				$boxes.prop('checked', true);
			}
		}
	},
	init: function() {
		$('.bulk-editor #toggle-check').on('change.bulkeditor', this.handlers.toggle_all);
		$('.bulk-editor li').on('click.bulkeditor', function() {
			var $box = $(this).find('input.bulk-select');
			$box.prop('checked', !$box.is(':checked'));
		});
		$('.bulk-editor li input.bulk-select').on('click.bulkeditor', function(e) {
			e.stopPropagation();
		});
	}
};

$(document).ready(function () {
	LinkEditor.init();
	BulkEditor.init();
});