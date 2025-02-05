98014 to 98368 206268m 128.91719 miles
74.5 miles via ferries
129 miles via ferries (Google Maps)
128 miles via ferries (Mapbox)

SELECT http_status_code, COUNT(http_status_code) FROM urls GROUP BY http_status_code ORDER BY COUNT(http_status_code) DESC;
 http_status_code | count 
------------------+-------
                0 |  1213
              200 |   113

113 * 144 = 16272 elements

https://console.mapbox.com/account/statistics

FAQ says to wait 24 hours to see updated stats

100,000 free requests per month
50,000 / 144 = 347

