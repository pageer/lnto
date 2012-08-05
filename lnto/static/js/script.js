$(document).ready(function () {
	$('.link-list .button.delete').click(function () {
		var $self = $(this),
		    link_name = $self.parents('li').find('.name').text();
		if (!confirm('Delete "'+link_name+'"?')) {
			return false;
		}
		var posturl = $self.attr('href');
		$.post(posturl, {}, function (data, textStatus, jzXHR) {
			if (data.status == 'success') {
				$self.parents('li').remove();
			} else {
				alert(data.message);
			}
		});
		return false;
	});
});