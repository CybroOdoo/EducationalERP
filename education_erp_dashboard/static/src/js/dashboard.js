/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, onWillUnmount } = owl
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";
import { useRef } from "@odoo/owl";

export class EducationalDashboard extends Component {
    /**
     * Sets up the Education Dashboard component.
     */
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
        this.orm = useService("orm");
        this.dashboard_templates = ['MainSection'];
        onWillStart(async () => {
            var self = this;
            this.props.title = 'Dashboard';
            $('.academic_exam_result').hide();
            $('.exam_result').show();
            $('.class_attendance_today').hide();
            $('.total_attendance_today').show();
        });
        onMounted(async () => {
            document.body.classList.add('o_education_dashboard_active');
            await this.render_graphs();
            this.fetch_data()
            await this.render_filters();
        });
        onWillUnmount(() => {
            document.body.classList.remove('o_education_dashboard_active');
        });
    }
    //    /* Orm call to fetch the count of applications, students, faculties,
    //    amenities and total exams */
    fetch_data() {
        var self = this;
        this.orm.call("erp.dashboard", "erp_data", []
        ).then(function (result) {
            $('#all_applications').append('<span>' + result.applications + '</span>');
            $('#all_students').append('<span>' + result.students + '</span>');
            $('#all_faculties').append('<span>' + result.faculties + '</span>');
            $('#all_amenities').append('<span>' + result.amenities + '</span>');
            $('#all_exams').append('<span>' + result.exams + '</span>');
            $('#all_promotions').append('<span>' + result.promotions + '</span>');
            $('#all_timetable').append('<span>' + result.timetable + '</span>');
            $('#all_attendance_count').append('<span>' + result.attendance + '</span>');
        });
    }
    change_select_period(e) {
        e.preventDefault();
        if (e.target.value == 'select') {
            $('.academic_exam_result').hide();
            $('.exam_result').show();
            this.render_exam_result_pie();
        }
        else {
            $('.exam_result').hide();
            $('.academic_exam_result').show();
            this.get_academic_exam_result(e.target.value);
        }
    }
    change_select_class(e) {
        e.preventDefault();
        if (e.target.value == 'select') {
            $('.class_attendance_today').hide();
            $('.total_attendance_today').show();
            this.render_attendance_doughnut();
        }
        else {
            $('.total_attendance_today').hide();
            $('.class_attendance_today').show();
            this.get_class_attendance(e.target.value);
        }
    }
    //    /* Functions that to show the details on click event */
    //    /* Click event function to show the applications */
    async onclick_application_list(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Applications",
            res_model: "education.application",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the students */
    onclick_student_list(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Students",
            res_model: "education.student",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the faculties */
    onclick_faculty_list(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Faculties",
            res_model: "education.faculty",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the amenities */
    onclick_amenity_list(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Amenities",
            res_model: "education.amenities",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the attendance list */
    onclick_attendance_list(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Attendance",
            res_model: "education.attendance",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the exam results */
    onclick_exam_result(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Exam Result",
            res_model: "education.exam",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Click event function to show the time table */
    onclick_timetable(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Timetable",
            res_model: "education.timetable",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    /* Click event function to show the promotions */
    onclick_promotions(e) {
        e.preventDefault();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Student Promotions",
            res_model: "education.student.final.result",
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            view_type: 'list',
            view_mode: 'list',
        });
    }
    //    /* Calling the functions to creates charts */
    render_graphs() {
        var self = this;
        self.render_total_application_graph();
        self.render_exam_result_pie();
        self.render_attendance_doughnut();
        self.render_rejected_accepted_applications();
        self.render_student_strength();
        self.render_class_wise_average_marks();
    }
    //    /* Calling the filter functions */
    render_filters() {
        var self = this;
        self.render_pie_chart_filter();
        self.render_doughnut_chart_filter();
    }
    /* Function to create a bar chart to show application counts in each
    academic year */
    render_total_application_graph() {
        var self = this
        var ctx = $(".application_count");
        this.orm.call("erp.dashboard", "get_all_applications", []
        ).then(function (result) {
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Application',
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c", "#2f4b7c", "#f95d6a", "#665191",
                            "#d45087", "#ff7c43", "#ffa600", "#a05195",
                            "#6d5c16", "#CCCCFF"
                        ],
                        borderColor: [
                            "#003f5c", "#2f4b7c", "#f95d6a", "#665191",
                            "#d45087", "#ff7c43", "#ffa600", "#a05195",
                            "#6d5c16", "#CCCCFF"
                        ],
                        borderWidth: 1, // Specify bar border width
                        type: 'bar', // Set this data to a line chart
                        fill: false
                    }]
                },
                //options to add appearance for the graph
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    /* Function to create a bar chart that shows the count of accepted and
    rejected applications */
    render_rejected_accepted_applications() {
        var self = this
        var ctx = $(".rejected_accepted_count");
        this.orm.call("erp.dashboard", "get_rejected_accepted_applications", []
        ).then(function (result) {
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Application',
                        data: Object.values(result),
                        backgroundColor: [
                            "#778899",
                            "#f08080",
                        ],
                        borderColor: [
                            "#778899",
                            "#f08080",
                        ],
                        borderWidth: 1
                    }]
                },
                //options to add appearance for the graph
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    /* Function to create a pie chart that shows the exam results */
    render_exam_result_pie() {
        var self = this;
        var ctx = $(".exam_result")[0].getContext('2d');
        // Check if chart exists and destroy it
        if (self.chart_total_result) {
            self.chart_total_result.destroy()
        }
        this.orm.call("erp.dashboard", "get_exam_result", []).then(function (result) {
            self.chart_total_result = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Exam Result',
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c",
                            "#dc143c"
                        ],
                        borderColor: [
                            "#003f5c",
                            "#dc143c",
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        })
    }
    /* Function to create a doughnut chart that shows attendance details */
    render_attendance_doughnut() {
        if (self.chart_total_attendance) {
            self.chart_total_attendance.destroy()
        }
        this.orm.call(
            "erp.dashboard",
            "get_attendance", []
        ).then(function (result) {
            var ctx = $(".total_attendance_today")[0].getContext('2d');
            var name = Object.keys(result)
            self.chart_total_attendance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: name,
                    datasets: [{
                        label: 'Attendance',
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c", "#2f4b7c", "#f95d6a", "#665191",
                            "#d45087", "#ff7c43", "#ffa600", "#a05195",
                            "#6d5c16", "#CCCCFF"
                        ],
                        borderColor: [
                            "#006400",
                            "#e9967a",
                        ],
                        barPercentage: 0.5,
                        barThickness: 6,
                        maxBarThickness: 8,
                        minBarLength: 0,
                        borderWidth: 1,
                        type: 'doughnut',
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        });
    }
    /* Function to create a line chart that shows the class wise student strength */
    render_student_strength() {
        var self = this
        var ctx = $(".student_strength");
        this.orm.call("erp.dashboard", "get_student_strength", []
        ).then(function (result) {
            var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Student Strength',
                        data: Object.values(result),
                        backgroundColor: [
                            "#8b0000"
                        ],
                        borderColor: [
                            "#8b0000"
                        ],
                        borderWidth: 1, // Specify bar border width
                    }]
                },
                //options to add appearance for the graph
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    //    /* Function to create a bar chart that shows the average marks in each class */
    render_class_wise_average_marks() {
        var self = this
        var ctx = $(".average_marks");
        this.orm.call(
            "erp.dashboard",
            "get_average_marks", []
        ).then(function (result) {
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Average Marks',
                        data: Object.values(result),
                        backgroundColor: [
                            "#cd5c5c"
                        ],
                        borderColor: [
                            "#cd5c5c",
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    //    /* Function to add the filter option */
    render_pie_chart_filter() {
        var self = this
        this.orm.call("erp.dashboard", "get_academic_year", []
        ).then(function (result) {
            $('#select_period').append('<option value=' + 'select' + '>' + 'Total Result' + '</option>')
            for (let key in result) {
                $('#select_period').append('<option value=' + key + '>' + result[key] + '</option>')
            }
        })
    }
    //   /* Function to get academic wise exam result and to create chart accordingly */
    get_academic_exam_result(academic_year) {
        var self = this;
        var ctx = $(".academic_exam_result")[0].getContext('2d');
        if (self.chart_academy_result) {
            self.chart_academy_result.destroy()
        }
        this.orm.call("erp.dashboard", "get_academic_year_exam_result", [academic_year]
        ).then(function (result) {
            self.chart_academy_result = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Exam Result',
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c",
                            "#dc143c"
                        ],
                        borderColor: [
                            "#003f5c",
                            "#dc143c",
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    //    /* Function to add filter option for doughnut chart */
    render_doughnut_chart_filter() {
        var self = this
        this.orm.call("erp.dashboard", "get_classes", []
        ).then(function (result) {
            $('#select_class').append('<option value=' + 'select' + '>' + 'Total Attendance' + '</option>')
            for (let key in result) {
                $('#select_class').append('<option value=' + key + '>' + result[key] + '</option>')
            }
        })
    }
    onChangeReportType(ev) {
        const selectedValue = ev.target.value;

        // Map dropdown values to tile IDs
        const visibleIds = {
            applications: "Applications",
            //        attendance: "all_attendance",
            students: "students",
            timetable: "timetable",
            promotion: "promotion",
            amenities: "amenities",
            all_attendance: "all_attendance",
            faculties: "faculties",
            exams: "exams",
            detailed: "promotion"  // or any other ID you use
        };

        const targetId = visibleIds[selectedValue];
        // Only select the dashboard cards, not the filters
        const dashboardTiles = document.querySelectorAll('.content-card');
        const graph = document.querySelectorAll('.inline');

        dashboardTiles.forEach(div => {
            if (targetId && div.id !== targetId) {
                div.style.display = "none";
            } else if (!targetId) {
                div.style.display = "block";  // If nothing selected, show all
            } else {
                div.style.display = "block";  // Show only matching tile
            }
        });
        graph.forEach(div => {
            if (targetId && div.id !== targetId) {
                div.style.display = "none";
            } else if (!targetId) {
                div.style.display = "block";  // If nothing selected, show all
            } else {
                div.style.display = "block";  // Show only matching tile
            }
        });
    }
    /* Function to get class wise attendance and to create chart accordingly */
    get_class_attendance(clas) {
        var self = this;
        var ctx = $(".class_attendance_today")[0].getContext('2d');
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        // Check if chart exists and destroy it
        if (self.chart_class_attendance) {
            self.chart_class_attendance.destroy();
        }
        this.orm.call("erp.dashboard", "get_class_attendance_today", [clas]).then(function (result) {
            self.chart_class_attendance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(result),
                    datasets: [{
                        label: 'Attendance',
                        data: Object.values(result),
                        backgroundColor: [
                            "#006400",
                            "#e9967a"
                        ],
                        borderColor: [
                            "#006400",
                            "#e9967a"
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        });
    }
}
EducationalDashboard.template = "EducationalDashboard"
registry.category("actions").add("erp_dashboard_tag", EducationalDashboard)
