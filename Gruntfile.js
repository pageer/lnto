module.exports = function(grunt) {

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-pylint');
    grunt.loadNpmTasks('grunt-nose');

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            all: ['Gruntfile.js', 'lnto/static/js/*.js']
        },
        pylint: {
            src_package: {
                src: 'lnto'
            },
            tests: {
                src: 'tests',
                options: {
                    disable: 'missing-docstring'
                }
            }
        },
        nose: {
            main: {
                src: 'tests/'
            }
        },
        copy: {
            main: {
                files: [
                    {
                        src: 'node_modules/jquery/dist/jquery.min.js',
                        dest: 'lnto/static/vendor/js/jquery.min.js'
                    }, {
                        src: 'node_modules/jquery-form/dist/jquery.form.min.js',
                        dest: 'lnto/static/vendor/js/jquery.form.min.js'
                    }, {
                        src: 'node_modules/jquery-ui-dist/jquery-ui.min.js',
                        dest: 'lnto/static/vendor/js/jquery-ui.min.js'
                    }, {
                        src: 'node_modules/tag-it/js/tag-it.min.js',
                        dest: 'lnto/static/vendor/js/tag-it.min.js'
                    }, {
                        src: 'node_modules/jquery-ui-dist/jquery-ui.min.css',
                        dest: 'lnto/static/vendor/css/jquery-ui.min.css'
                    }, {
                        src: 'node_modules/jquery-ui-dist/jquery-ui.structure.min.css',
                        dest: 'lnto/static/vendor/css/jquery-ui.structure.min.css'
                    }, {
                        src: 'node_modules/jquery-ui-dist/jquery-ui.theme.min.css',
                        dest: 'lnto/static/vendor/css/jquery-ui.theme.min.css'
                    }, {
                        src: 'node_modules/tag-it/css/jquery.tagit.css',
                        dest: 'lnto/static/vendor/css/jquery.tagit.css'
                    }, {
                        src: 'node_modules/tag-it/css/tagit.ui-zendesk.css',
                        dest: 'lnto/static/vendor/css/tagit.ui-zendesk.css'
                    }
                ]
            }
        }
    });

    grunt.registerTask('lint', ['jshint', 'pylint']);
    grunt.registerTask('test', ['nose']);
    grunt.registerTask('validate', ['jshint', 'pylint', 'nose']);
    grunt.registerTask('deploy', ['copy']);
    grunt.registerTask('default', ['jshint', 'pylint', 'nose', 'copy']);
};
