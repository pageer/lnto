module.exports = function(grunt) {

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-pylint');
    grunt.loadNpmTasks('grunt-bower');
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
        bower: {
            dev: {
                dest: 'lnto/static/vendor/',
                js_dest: 'lnto/static/vendor/js/',
                css_dest: 'lnto/static/vendor/css/',
                options: {
                    keepExpandedHierarchy: false,
                    packageSpecific: {
                        jquery: {
                            files: ['dist/jquery.min.js']
                        },
                        'jquery-form': {
                            files: ['dist/jquery.form.min.js']
                        }
                    }
                }
            }
        }
    });

    grunt.registerTask('lint', ['jshint', 'pylint']);
    grunt.registerTask('test', ['nose']);
    grunt.registerTask('validate', ['jshint', 'pylint', 'nose']);
    grunt.registerTask('deploy', ['bower']);
    grunt.registerTask('default', ['jshint', 'pylint', 'nose', 'bower']);
};
