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
