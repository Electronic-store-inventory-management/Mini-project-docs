\# US-24 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Performance and Load Validation



**GitHub Issue:** #39

\*\*Project:\*\* Electronics Store Inventory Management System



\## 1. Objective



To validate application performance under concurrent access and a large inventory dataset. The objective was to simulate up to 10 concurrent users, test with 10,000 component records and verify that the 90th percentile response time remains within 3 seconds.



\## 2. Testing Environment



\- Application: Django

\- Database: MySQL 8.0.46

\- Load testing tool: Locust 2.47.0

\- Application server: Waitress

\- Virtual users: 10

\- Test duration: 120 seconds

\- Spawn rate: 2 users per second

\- Inventory dataset: 10,000 component records

\- Database used: electronics\_inventory\_perf



A separate performance database was used to avoid affecting normal inventory data.



\## 3. Testing Methodology



Locust simulated 10 concurrent users accessing the application.



The following operations were tested:



1\. User login and authentication.

2\. Component inventory listing.

3\. Component search by component ID, name and category.

4\. Component availability.

5\. Low-stock component listing.

6\. Out-of-stock component listing.

7\. Dashboard statistics.



\## 4. Initial Performance Bottlenecks



The initial test identified slow response times because the application rendered large numbers of component records in a single request.



Initial aggregated p90 response time was approximately 41 seconds.



Major bottlenecks:

\- Component listing: 42 seconds p90.

\- Component search: 43 seconds p90.

\- Component availability: 28 seconds p90.



\## 5. Optimisation Implemented



Pagination was implemented using Django's Paginator.



\- Limited displayed records to 50 per page.

\- Added search filtering across component ID, name and category.

\- Applied pagination to inventory listing, availability, low-stock and out-of-stock pages.

\- Preserved existing inventory information and access restrictions.



\## 6. Final Performance Results



The final test completed with 10 concurrent users and 10,000 component records.



| Operation | Requests | P90 response time |

|---|---:|---:|

| Login | 10 | 2,200 ms |

| Login page | 10 | 24 ms |

| Dashboard | 52 | 150 ms |

| Component list | 227 | 130 ms |

| Component search | 120 | 160 ms |

| Availability | 143 | 120 ms |

| Low stock | 102 | 110 ms |

| Out of stock | 95 | 97 ms |

| \*\*Aggregated\*\* | \*\*759\*\* | \*\*140 ms\*\* |



Additional results:

\- Failed requests: 0

\- Maximum response time: 2,214 ms

\- Aggregated average response time: approximately 118 ms.



\## 7. Before and After Comparison



| Metric | Before | After |

|---|---:|---:|

| Aggregated p90 | 41,000 ms | 140 ms |

| Component list p90 | 42,000 ms | 130 ms |

| Component search p90 | 43,000 ms | 160 ms |

| Availability p90 | 28,000 ms | 120 ms |



The aggregated p90 response time improved by approximately 99.66%.



\## 8. Acceptance Criteria Verification



1\. Test up to 10 concurrent users ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Completed.

2\. Test with up to 10,000 component records ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Completed.

3\. Measure representative operation response times ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Completed.

4\. Verify p90 response time within 3 seconds ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Passed.

5\. Document performance results and bottlenecks ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Completed.



\*\*Final aggregated p90: 140 ms (0.14 seconds).\*\*



The required threshold was 3,000 ms. All measured operation-specific p90 values were also below 3,000 ms.



\## 9. Conclusion



The initial performance test identified significant delays when rendering the complete inventory. After implementing pagination and search filtering, the application achieved substantially faster response times.



The final load test completed successfully with 10 concurrent virtual users, 10,000 component records and zero failed requests. The 90th percentile response time was 140 ms, satisfying the performance requirement.



The results represent a local test environment and should not be interpreted as a production capacity guarantee.



\## 10. Test Evidence



\- `results/us24.html` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Initial performance report.

\- `results/us24\_stats.csv` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Initial response statistics.

\- `results/us24\_final.html` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Final performance report.

\- `results/us24\_final\_stats.csv` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Final response statistics.

\- `results/us24\_final\_stats\_history.csv` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Response-time history.
