<canvas id="myChart"></canvas>
<canvas id="salaryTrendsChart" width="400" height="200"></canvas>
<canvas id="vacancyTrendsChart" width="400" height="200"></canvas>
<canvas id="salaryByCityChart" width="400" height="200"></canvas>
<canvas id="vacancyShareByCityChart" width="400" height="200"></canvas>
<canvas id="topSkillsChart" width="400" height="200"></canvas>


    const ctx = document.getElementById('myChart').getContext('2d');
    const topSkillsData = {
        labels: [
            {% for skill in top_skills %}
                '{{ skill.0 }}'{% if not forloop.last %}, {% endif %}
            {% endfor %}
        ],
        datasets: [{
            label: 'Частота',
            data: [
                {% for skill in top_skills %}
                    {{ skill.1 }}{% if not forloop.last %}, {% endif %}
                {% endfor %}
            ],
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
        }]
    };

    const myChart = new Chart(ctx, {
        type: 'bar',
        data: topSkillsData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
        const salaryTrendsData = {
            labels: {{ salary_trends.keys|safe }},
            datasets: [{
                label: 'Средняя зарплата (руб.)',
                data: {{ salary_trends.values|safe }},
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 1
            }]
        };

        const vacancyTrendsData = {
            labels: {{ vacancy_trends.keys|safe }},
            datasets: [{
                label: 'Количество вакансий',
                data: {{ vacancy_trends.values|safe }},
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderWidth: 1
            }]
        };

        const salaryByCityData = {
            labels: {{ salary_by_city.keys|safe }},
            datasets: [{
                label: 'Средняя зарплата (руб.)',
                data: {{ salary_by_city.values|safe }},
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        };

        const vacancyShareByCityData = {
            labels: {{ vacancy_share_by_city.keys|safe }},
            datasets: [{
                label: 'Количество вакансий',
                data: {{ vacancy_share_by_city.values|safe }},
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1
            }]
        };

       const topSkillsData = {
           labels: [
               {% for skill in top_skills %}
                   '{{ skill.0 }}'{% if not forloop.last %}, {% endif %}
               {% endfor %}
           ],
           datasets: [{
               label: 'Частота',
               data: [
                   {% for skill in top_skills %}
                       {{ skill.1 }}{% if not forloop.last %}, {% endif %}
                   {% endfor %}
               ],
               backgroundColor: 'rgba(153, 102, 255, 0.2)',
               borderColor: 'rgba(153, 102, 255, 1)',
               borderWidth: 1
           }]
       };

        const ctxSalaryTrends = document.getElementById('salaryTrendsChart').getContext('2d');
        new Chart(ctxSalaryTrends, {
            type: 'line',
            data: salaryTrendsData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        const ctxVacancyTrends = document.getElementById('vacancyTrendsChart').getContext('2d');
        new Chart(ctxVacancyTrends, {
            type: 'line',
            data: vacancyTrendsData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                 }
            }
        });

        const ctxSalaryByCity = document.getElementById('salaryByCityChart').getContext('2d');
        new Chart(ctxSalaryByCity, {
            type: 'bar',
            data: salaryByCityData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        const ctxVacancyShareByCity = document.getElementById('vacancyShareByCityChart').getContext('2d');
        new Chart(ctxVacancyShareByCity, {
            type: 'bar',
            data: vacancyShareByCityData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        const ctxTopSkills = document.getElementById('topSkillsChart').getContext('2d');
        new Chart(ctxTopSkills, {
            type: 'horizontalBar',
            data: topSkillsData,
            options: {
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });

