$(function () {

  $(".js-create-categoria").click(function () {

    $.ajax({
      url: '/categoriasalarial/create/',
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-categoria").modal("show");
      },
      success: function (data) {
        $("#modal-categoria .modal-content").html(data.html_form);
      }
    });
  });

});