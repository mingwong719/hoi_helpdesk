/** @odoo-module */

import {  useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";
import { cookie } from "@web/core/browser/cookie";
const { Component, useState, onWillUpdateProps ,onWillStart, useRef, onWillUnmount, useEffect} = owl;

export class RTHelpdeskDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");

        // ELEMENT REFERENCES
        this.dashboard_nav_tabs = useRef('dashboard_nav_tabs');
        this.dashboard_section = useRef('dashboard_section');
        this.dashboard_show_button = useRef('dashboard_show_button');
        this.canvas_stage_id_ref = useRef("canvas_stage_id");        
        this.canvas_direction_ref = useRef("canvas_direction");        
        // ELEMENT REFERENCES
        this.chart_stage_id = null;
        this.chart_direction = null;

        var view_dashboard_active_tab = localStorage.getItem("rt_helpdesk_view_dashboard_active_tab");
        // By default, data tab is active
        if (!view_dashboard_active_tab) {
            view_dashboard_active_tab = "data active show";
        }

        var view_dashboard_style_display_property_value = !!localStorage.getItem("rt_helpdesk_view_dashboard_is_shown") ? "block" : "none";
        var view_dashboard_show_toggle_button_string = _t("Show Dashboard");
        if (view_dashboard_style_display_property_value == 'block') {
            view_dashboard_show_toggle_button_string = _t("Hide Dashboard");
        }

        this.state = useState({
            infos: {},
            css:{
                'view_dashboard_style_display_property_value':  view_dashboard_style_display_property_value,
                'view_dashboard_active_tab': view_dashboard_active_tab,
                'view_dashboard_show_toggle_button_string':view_dashboard_show_toggle_button_string,
            },
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this._fetch_rt_helpdesk_dashboard_data([this.props.domain])
        });
        onWillUpdateProps(this.willUpdate);
        useEffect(() => this.renderChart());
        onWillUnmount(this.onWillUnmount);

    }
    onWillUnmount() {
        if (this.chart_stage_id) {
            this.chart_stage_id.destroy();
        }
        if (this.chart_direction) {
            this.chart_direction.destroy();
        }
    }


    /**
     * Creates and binds the chart on `canvasRef`.
     */
    renderChart() {
        if (this.chart_stage_id) {
            this.chart_stage_id.destroy();
        }

        if (this.chart_direction) {
            this.chart_direction.destroy();
        }

        const ctx_canvas_stage_id = this.canvas_stage_id_ref.el.getContext('2d');
        this.chart_stage_id = new Chart(ctx_canvas_stage_id, this._get_bar_chart_config());

        const ctx_canvas_direction = this.canvas_direction_ref.el.getContext('2d');
        this.chart_direction = new Chart(ctx_canvas_direction, this._get_doughnut_chart_config());

    }

        /**
         * doughnut chart config for direction
         */

        _get_doughnut_chart_config() {
            var self = this;
            var background_color = [];
            // Process country data to fit into the ChartJS scheme
            var labels = [];
            var data = [];
            for (var i = 0; i < self.state.infos.list_of_direction_count_dic.length; i++) {
                labels.push(self.state.infos.list_of_direction_count_dic[i]["name"]);
                data.push(self.state.infos.list_of_direction_count_dic[i]["count"]);
                var color = self.state.infos.list_of_direction_count_dic[i]["classes"] === "bg-danger" ? "#dc3545" : self.state.infos.list_of_direction_count_dic[i]["classes"] === "bg-success" ? "#28a745" : "#343a40";
                background_color.push(color);
            }

            return {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "",
                            data: data,
                            backgroundColor: background_color,
                            // borderColor: 'rgba(0, 0, 0, 0.1)'
                        },
                    ],
                },
                options: {
                    maintainAspectRatio: false,
                    legend: {
                        display: true,
                    },
                    title: {
                        display: false,
                        text: _t("Overall Performance"),
                    },
                    layout: {
                        padding: {
                            left: 10,
                            right: 10,
                            top: 10,
                            bottom: 10,
                        },
                    },
                },
            };
        }


        /**
         * bar chart config for ticket stage_id
         */


    /**
     * Custom bar chart configuration for our survey session use case.
     *
     * Quick summary of enabled features:
     * - background_color is one of the 10 custom colors from SESSION_CHART_COLORS
     *   (see _getBackgroundColor for details)
     * - The ticks are bigger and bolded to be able to see them better on a big screen (projector)
     * - We don't use tooltips to keep it as simple as possible
     * - We don't set a suggestedMin or Max so that Chart will adapt automatically based on the given data
     *   The '+1' part is a small trick to avoid the datalabels to be clipped in height
     * - We use a custom 'datalabels' plugin to be able to display the number value on top of the
     *   associated bar of the chart.
     *   This allows the host to discuss results with attendees in a more interactive way.
     *
     * @private
     */
    _get_bar_chart_config() {     
        var self = this;
        var background_color = [];
        // Process data to fit into the ChartJS scheme
        var labels = [];
        var data = [];
        // var legend_labels = [];
        for (var i = 0; i < this.state.infos.list_of_stage_id_count_dic.length; i++) {
            labels.push(this.state.infos.list_of_stage_id_count_dic[i]["name"]);
            data.push(this.state.infos.list_of_stage_id_count_dic[i]["count"]);
            background_color.push(this.state.infos.list_of_stage_id_count_dic[i]["color_html"]);
        }

        return {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    backgroundColor:background_color,
                    data: data,
                }]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Ticket Stages"),
                    },
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        enabled: true,             
                    },
                },
                scales: {
                    y: {
                        ticks: {
                            display: true,
                        },
                        grid: {
                            display: true
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 0,
                            font: {
                                size :"12",
                                weight:"normal"
                            },
                            color : '#212529'
                        },                    
                        grid: {
                            drawOnChartArea: false,
                            color: 'rgba(0, 0, 0, 0.2)'
                        }
                    }
                },
            },
            plugins: [{
                /**
                 * The way it works is each label is an array of words.
                 * eg.: if we have a chart label: "this is an example of a label"
                 * The library will split it as: ["this is an example", "of a label"]
                 * Each value of the array represents a line of the label.
                 * So for this example above: it will be displayed as:
                 * "this is an examble<br/>of a label", breaking the label in 2 parts and put on 2 lines visually.
                 *
                 * What we do here is rework the labels with our own algorithm to make them fit better in screen space
                 * based on breakpoints based on number of columns to display.
                 * So this example will become: ["this is an", "example of", "a label"] if we have a lot of labels to put in the chart.
                 * Which will be displayed as "this is an<br/>example of<br/>a label"
                 * Obviously, the more labels you have, the more columns, and less screen space is available.
                 *
                 * When the screen space is too small for long words, those long words are split over multiple rows.
                 * At 6 chars per row, the above example becomes ["this", "is an", "examp-", "le of", "a label"]
                 * Which is displayed as "this<br/>is an<br/>examp-<br/>le of<br/>a label"
                 * 
                 * We also adapt the font size based on the width available in the chart.
                 *
                 * So we counterbalance multiple times:
                 * - Based on number of columns (i.e. number of survey.question.answer of your current survey.question),
                 *   we split the words of every labels to make them display on more rows.
                 * - Based on the width of the chart (which is equivalent to screen width),
                 *   we reduce the chart font to be able to fit more characters.
                 * - Based on the longest word present in the labels, we apply a certain ratio with the width of the chart
                 *   to get a more accurate font size for the space available.
                 *
                 * @param {Object} chart
                 */
                beforeInit: function (chart) {
                    const nbrCol = chart.data.labels.length;
                    const minRatio = 0.4;
                    // Numbers of maximum characters per line to print based on the number of columns and default ratio for the font size
                    // Between 1 and 2 -> 25, 3 and 4 -> 20, 5 and 6 -> 15, ...
                    const charPerLineBreakpoints = [
                        [1, 2, 25, minRatio],
                        [3, 4, 20, minRatio],
                        [5, 6, 15, 0.45],
                        [7, 8, 10, 0.65],
                        [9, null, 7, 0.7],
                    ];

                    let charPerLine;
                    let fontRatio;
                    charPerLineBreakpoints.forEach(([lowerBound, upperBound, value, ratio]) => {
                        if (nbrCol >= lowerBound && (upperBound === null || nbrCol <= upperBound)) {
                            charPerLine = value;
                            fontRatio = ratio;
                        }
                    });

                    // Adapt font size if the number of characters per line is under the maximum
                    if (charPerLine < 25) {
                        const allWords = chart.data.labels.reduce((accumulator, words) => accumulator.concat(' '.concat(words)));
                        const maxWordLength = Math.max(...allWords.split(' ').map((word) => word.length));
                        fontRatio = maxWordLength > charPerLine ? minRatio : fontRatio;
                        chart.options.scales.x.ticks.font.size = Math.min(parseInt(chart.options.scales.x.ticks.font.size), chart.width * fontRatio / (nbrCol));
                    }

                    chart.data.labels.forEach(function (label, index, labelsList) {
                        // Split all the words of the label
                        const words = label.split(" ");
                        let resultLines = [];
                        let currentLine = [];
                        for (let i = 0; i < words.length; i++) {
                            // Chop down words that do not fit on a single line, add each part on its own line.
                            let word = words[i];
                            while (word.length > charPerLine) {
                                resultLines.push(word.slice(0, charPerLine - 1) + '-');
                                word = word.slice(charPerLine - 1);
                            }
                            currentLine.push(word);

                            // Continue to add words in the line if there is enough space and if there is at least one more word to add
                            const nextWord = i+1 < words.length ? words[i+1] : null;
                            if (nextWord) {
                                const nextLength = currentLine.join(' ').length + nextWord.length;
                                if (nextLength <= charPerLine) {
                                    continue;
                                }
                            }
                            // Add the constructed line and reset the variable for the next line
                            const newLabelLine = currentLine.join(' ');
                            resultLines.push(newLabelLine);
                            currentLine = [];
                        }
                        labelsList[index] = resultLines;
                    });
                },
            }],
        };
    }




    onClickShowDashboard() {
        if (this.state.css.view_dashboard_style_display_property_value == 'block'){
            this.state.css.view_dashboard_style_display_property_value = 'none';
            this.state.css.view_dashboard_show_toggle_button_string = _t("Show Dashboard");
            localStorage.removeItem("rt_helpdesk_view_dashboard_is_shown"); 
        }else{
            this.state.css.view_dashboard_style_display_property_value = 'block';
            this.state.css.view_dashboard_show_toggle_button_string = _t("Hide Dashboard");            
            localStorage.setItem("rt_helpdesk_view_dashboard_is_shown", "true");               
        }
    }


    /**
     * Fires when click on tab pane anchor button
     * Store active tab in local storage in order to open that
     * tab when page refresh
     *
     * @private
     * @param {MouseEvent} ev
     */
    onClickViewDashboardNavTabAnchor(active_tab) {       
        if (this.chart_stage_id) {
            this.chart_stage_id.update();
        }

        if (this.chart_direction) {
            this.chart_direction.update();
        }
                
        // var active_tab = $(ev.currentTarget).attr("data-js_tab_name");
        this.state.css.view_dashboard_active_tab = active_tab;
        localStorage.setItem("rt_helpdesk_view_dashboard_active_tab", active_tab);
    }

    async willUpdate(nextProps) {
        await this._fetch_rt_helpdesk_dashboard_data([nextProps.domain])
    }

    async _fetch_rt_helpdesk_dashboard_data(domain = []) {
        this.state.infos = await this.orm.call(
            "rt.helpdesk.ticket",
            "get_ticket_dashboard",
            domain
        );
    }
}

RTHelpdeskDashboard.props = ["domain"];
RTHelpdeskDashboard.template = 'rt_helpdesk.RTHelpdeskDashboard';