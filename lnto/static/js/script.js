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
			$.post(posturl, {}, function (data, textStatus, jzXHR) {
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

$(document).ready(function () {
	LinkEditor.init();
});