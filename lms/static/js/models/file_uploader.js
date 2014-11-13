(function(Backbone) {
    var FileUploaderModel = Backbone.Model.extend({
        defaults: {
            title: '',
            description: '',
            extension: '',
            url: '',
            result: ''
        }
    });

    this.FileUploaderModel = FileUploaderModel;
}).call(this, Backbone);
