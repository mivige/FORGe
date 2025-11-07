classification matrix that is designed to help categorize customer requests


| Main Category | Subcategory | Example Customer Request | Department/Handling Group |
| :-- | :-- | :-- | :-- |
| Billing \& Payments | Duplicate Charges | "Why did I get charged twice this month?" | Billing/Finance |
|  | Refund Requests | "I want a refund for my last order." | Billing/Finance |
|  | Payment Methods | "Can I update my credit card information?" | Billing/Finance |
|  | Invoice Requests | "Can you send me an invoice for my recent purchase?" | Billing/Finance |
| Account Management | Password Reset | "I forgot my password, can you help me reset it?" | Account Support |
|  | Account Setup/Activation | "How do I create a new account?" | Account Support |
|  | Account Cancellation | "I want to close my account." | Account Support |
|  | Upgrade/Downgrade Plans | "How can I upgrade my subscription?" | Sales/Account Management |
| Product/Service Inquiry | Product Availability | "Is this item available in my country?" | Sales/Product Info |
|  | Product Features | "What features does the premium plan include?" | Sales/Product Info |
|  | Service Coverage | "Do you offer support in my area?" | Sales/Product Info |
| Technical Support | Device Issues | "My smartphone won't charge." | Technical Support |
|  | Software Problems | "The app crashes when I try to open it." | Technical Support |
|  | Connectivity Problems | "I am experiencing network outages." | Technical Support |
|  | Installation Help | "How do I install the software on my PC?" | Technical Support |
| Order \& Shipping | Order Status | "Where is my order? It’s late." | Order Fulfillment |
|  | Shipping Delays | "My shipment hasn't arrived yet." | Order Fulfillment |
|  | Returns \& Exchanges | "How do I return an item I purchased?" | Order Fulfillment |
| Complaints \& Feedback | Product Quality | "The product I received is damaged." | Customer Relations |
|  | Service Complaints | "Your support was very unhelpful." | Customer Relations |
|  | Suggestions | "I have an idea to improve your service." | Customer Relations |
| Follow-up Requests | Case Updates | "I want an update on my previous support ticket." | Support/Follow-up |
|  | Escalations | "I need to speak to a supervisor regarding unresolved issues." | Escalation Team |
| Service Outages | Local Outages | "My internet is down in my area." | Technical Support/Network |
|  | Widespread Outages | "Is your service down nationwide?" | Technical Support/Network |
| General FAQs | Hours of Operation | "What are your business hours?" | Automated Response/Help Desk |
|  | Account Management FAQs | "How do I change my email address?" | Automated Response/Help Desk |
|  | Basic Troubleshooting | "How to reset my router?" | Automated Response/Help Desk |

### Notes for LLM and Unsupervised Learning Model:

- Each request can be vectorized by the LLM in NLP-embedding space, and its similarity to example phrases per subcategory can be used for classification.
- The granularity allows distinguishing subtle differences (e.g., refund vs. invoice requests in billing).
- Department routes (final column) serve as labels to cluster or classify customer intents based on embeddings.
- Unsupervised models can learn groupings around these labeled intents, allowing scale and adaptability for new unseen requests.


