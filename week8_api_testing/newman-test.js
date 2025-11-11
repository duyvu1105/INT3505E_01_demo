const newman = require('newman');

// Chạy Newman bằng API
newman.run({
    collection: 'Week8.postman_collection.json',             // file collection
    environment: 'New_Environment.postman_environment.json', // file environment
    reporters: ['cli', 'htmlextra'],                         // định dạng report
    iterationCount: 5,                                       // tương đương -n 5
    reporter: {
        htmlextra: {
            export: 'test_report.html',                      // nơi lưu report HTML
            title: 'API Test Report',                        // (tùy chọn) tiêu đề report
            browserTitle: 'Newman HTML Report'               // (tùy chọn)
        }
    }
}, function (err, summary) {
    if (err) {
        console.error('Error running collection:', err);
        process.exit(1);
    }

    console.log('Collection run complete!');
    if (summary.run.failures.length > 0) {
        console.log('Some tests failed!');
        process.exit(1);
    } else {
        console.log('All tests passed successfully!');
    }
});
