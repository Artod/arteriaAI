# MLOps pipeline for PDF file processing (ArteriaAI)

## Introduction
The designed pipeline serves as a sophisticated system intended for the efficient processing of PDF documents in a cloud environment, with a specific focus on extracting meaningful insights through machine learning techniques. This pipeline is a component of a broader document understanding product envisioned by ArteriaAI. It has been meticulously structured to address two primary use cases, thereby enhancing the accessibility of documents for downstream tasks and facilitating advanced search capabilities through vector embeddings.

## System Overview

High-level architecture diagram showing the flow from document upload to result retrieval.

![arch](/diagram.jpg)

## Use cases

The pipeline supports two critical use cases:

1. **Document Processing and Embedding Generation:** When a user uploads a PDF file to an S3 bucket, this triggers an event that sends a message to SQS. An AWS Lambda function (referred to as the "worker") is then triggered to process this message. The worker downloads the file, parses the text, and sends a request to Amazon Sagemaker to generate embeddings for the text. These embeddings, alongside their associated text chunks, are then saved in Pinecone, a vector database. This process essentially transforms the document into a searchable, vectorized format that can be easily accessed and analyzed for various downstream tasks.

2. **Retrieving Top Results from Embeddings:** Users can query the system to retrieve the top 5 most relevant pieces of content from the processed documents based on their search criteria. Another AWS Lambda function (referred to as the "query" lambda) is exposed through an API Gateway. This lambda makes a request to Sagemaker to convert the search query into a vector and then queries Pinecone to retrieve the top 5 results based on the vector similarities. This use case is pivotal for enabling advanced search functionalities, allowing users to quickly find the most relevant document segments based on their query.

## Component Descriptions
### AWS S3 (Document Storage)

Amazon S3 is chosen as the document storage solution for several compelling reasons directly aligned with the project's needs:

- **Scalability:** S3's scalability is unmatched, allowing it to handle from one to millions of files without any degradation in performance. This capability directly addresses the requirement for handling variable volumes of document uploads, which can range from a single file to thousands in a short time span.

- **Cost Efficiency:** S3 offers a pay-as-you-go model that ensures cost efficiency, especially important given the variable frequency and volume of document submissions described. This model allows for cost-effective storage management that scales with the project's needs.

- **Market Leadership:** AWS's position as a market leader in cloud services provides a level of reliability and security that's critical for handling sensitive document processing tasks. The extensive documentation, support, and integration capabilities with other AWS services, like SQS and Lambda, make it a logical choice for ensuring a seamless and robust pipeline.

- **Event-Driven Processing Integration:** S3's ability to trigger events upon file upload is a crucial feature for the pipeline. It allows for the automation of subsequent steps, such as message queuing in SQS and processing in Lambda, without manual intervention. This integration capability fulfills the need for an efficient, automated workflow that minimizes latency and maximizes throughput.

These reasons collectively justify the selection of AWS S3 as the foundational storage component of the document processing pipeline, ensuring it meets the project's scalability, cost, reliability, and automation requirements.

###  AWS SQS (Message Queuing Service)
AWS Simple Queue Service (SQS) is strategically selected for its critical role in the document processing pipeline, primarily facilitating the decoupling of document upload and processing tasks. This choice is underpinned by two key advantages that align perfectly with the pipeline's requirements:

- **Decoupling for Scalability:** SQS effectively separates the document upload event in S3 from the processing tasks handled by Lambda functions. This decoupling is essential for scalability, as it allows each component to operate independently, scaling up or down based on demand. For instance, if there's a surge in document uploads, SQS queues can accumulate messages without overloading the processing workers, ensuring that the system remains responsive and efficient regardless of load variations.

- **Error Handling and Retries:** Given that file processing involves multiple steps—each susceptible to errors—SQS provides a robust mechanism for managing failures. If a processing step fails, the message remains in the queue and can be retried. This ability to retry from previous steps without losing data or state ensures that temporary issues (like transient errors in external services or temporary resource constraints) can be overcome without manual intervention. Furthermore, SQS's dead-letter queue capabilities allow for the segregation of problematic messages that repeatedly fail, enabling focused troubleshooting without disrupting the overall processing flow.

The integration of SQS into the pipeline not only enhances its resilience and fault tolerance but also optimizes resource utilization and operational efficiency. This aligns with the project's goals of building a system that is both scalable and reliable, capable of handling variable workloads with minimal manual oversight.

###  AWS Lambda (Processing Workers)
AWS Lambda is employed as the backbone for processing tasks within the pipeline, distinguished by its serverless architecture that offers both scalability and cost efficiency. The worker Lambda functions are triggered by messages from AWS SQS, ensuring a smooth workflow that automatically processes documents as they are queued. The processing consists of four key steps:

1. **Document Downloading:** Upon trigger, the Lambda function retrieves the PDF document from S3 using the information specified in the SQS message.

1. **Document Parsing:** The function then parses the document to extract text. This step is crucial for converting the PDF into a format suitable for further analysis and processing.

1. **Embedding Generation:** Once the text is extracted, the Lambda interacts with Amazon Sagemaker, leveraging a pre-trained machine learning model to convert the text into vector embeddings. This transformation is key for enabling sophisticated search and analysis capabilities.

1. **Storing Results in Pinecone:** The final step involves saving the generated embeddings along with their associated text chunks into Pinecone. This vector database is chosen for its ability to efficiently handle similarity searches, making it an ideal storage solution for the embeddings.

The use of AWS Lambda for these processing tasks is justified by several factors:

- **Scalability:** Lambda functions automatically scale with the incoming workload, which means they can handle a few to thousands of document processing tasks without any configuration changes. This scalability is crucial for dealing with variable document upload volumes.

- **Cost Efficiency:** With Lambda, you pay only for the compute time you consume, making it an economical choice for processing tasks that might not be constant. This cost model aligns with the project's need for an efficient, cost-effective solution.

- **Integration and Automation:** Lambda's seamless integration with other AWS services like SQS for triggering and S3 for storage simplifies the architecture and automates the document processing workflow, minimizing manual management and potential errors.

Overall, AWS Lambda's inclusion in the pipeline underscores a commitment to building a responsive, efficient, and cost-effective document processing system.

### Amazon Sagemaker (Embedding Generation)
Amazon Sagemaker is integral to the pipeline for generating vector embeddings from text, leveraging its powerful machine learning capabilities. This service is chosen for several key attributes that align with the pipeline’s requirements for efficiency, scalability, and ease of management:

- **Scalability:** Sagemaker easily scales to accommodate varying workloads, from small-scale document processing tasks to large batches requiring intensive computational resources. This scalability ensures that embedding generation can keep pace with the document processing pipeline's needs, regardless of the volume or complexity of the documents being processed.

- **Managed Service:** As a fully managed service, Sagemaker significantly economizes the time and effort required for setup and maintenance. This is particularly advantageous for startups and enterprises looking to minimize operational overhead while leveraging advanced machine learning models for embedding generation. The service manages the underlying infrastructure, model tuning, optimization, and deployment, allowing teams to focus on developing and refining their applications.

However, the choice of Sagemaker does come with considerations:

- **Cost:** While offering substantial benefits in terms of scalability and ease of management, Sagemaker can be costlier than managing your own machine learning infrastructure, especially at scale. The pricing model, which charges for computation time and data throughput, might lead to higher operational costs for extensive processing tasks.

- **Optimization for Cost Efficiency:** To mitigate these costs, alternatives such as utilizing Amazon EC2 instances with custom machine learning environments can be considered. By managing your own instances, you gain finer control over the computational resources and can optimize the infrastructure for cost efficiency. Implementing spot instances, reserved instances, or leveraging containerized machine learning models on Amazon ECS or EKS are strategies that can offer more cost-effective solutions without significantly compromising on scalability or performance.

Despite these considerations, Amazon Sagemaker’s role in the pipeline is justified by its immediate impact on accelerating development cycles, reducing the time to market, and enabling the focus on core product functionalities rather than infrastructure management. Future optimizations could explore a hybrid approach, balancing between Sagemaker for its managed services and custom solutions for cost efficiency.

### Pinecone (Vector Database)
Pinecone is selected as the vector database for storing and querying vector embeddings generated from the document processing pipeline. This choice is driven by Pinecone's unique capabilities and alignment with the project’s requirements for high performance, scalability, and ease of development:

- **Purpose-Built for Vector Search:** Unlike traditional databases designed for scalar data, Pinecone is engineered from the ground up specifically for vector search. This specialization ensures exceptional performance in retrieving the top 5 most relevant vector embeddings in real-time, a requirement highlighted in the project specifications. Its architecture is optimized for the unique challenges of vector search, including high-dimensional data and similarity search, making it supremely efficient for the pipeline’s needs.

- **Scalability and Real-Time Performance:** Pinecone's scalability is a critical factor in its selection. It can effortlessly scale to handle large datasets and high query volumes without compromising on performance. This capability is vital for maintaining real-time response times when querying the top results, ensuring that the system can deliver fast and accurate search results even as the volume of processed documents grows.

- **Serverless and Development Speed:** As a serverless platform, Pinecone significantly reduces the operational overhead associated with managing vector databases. This aspect is particularly beneficial for rapid development and deployment, as it eliminates the need for provisioning, scaling, and maintaining the underlying infrastructure. The serverless model not only accelerates the development cycle but also ensures cost efficiency by automatically scaling resources to match the demand.

- **Integration and Ease of Use:** Pinecone offers simple and straightforward integration with existing cloud services and the broader technology stack of the pipeline. Its APIs facilitate easy ingestion of vector embeddings and querying of the database, simplifying the development process and allowing the team to focus on optimizing the core functionalities of the pipeline.

Choosing Pinecone addresses the project's requirement for a database that can offer real-time performance for vector search queries, support scalable operations, and facilitate a swift development process. Its purpose-built nature for vector search, combined with serverless architecture, positions Pinecone as an ideal solution for enhancing the pipeline’s capabilities in handling advanced document search and analysis tasks.

### AWS API Gateway and Lambda (Query Service)
The combination of AWS API Gateway and Lambda forms the backbone of the query service in the pipeline, enabling users to retrieve the top 5 most relevant results from Pinecone based on their search queries. This setup is selected for its inherent scalability, ease of management, and seamless integration capabilities:

- **Functionality:** The query service operates by accepting user queries through the API Gateway, which then triggers a Lambda function. This function is responsible for converting the query into a vector using the same logic as the document processing workflow, and subsequently querying Pinecone to retrieve and return the most relevant results. This design ensures a cohesive and efficient process from query reception to response delivery.

- **Scalability of API Gateway:** AWS API Gateway is inherently scalable, capable of handling thousands of concurrent API calls without any additional configuration. This scalability ensures that the query service can accommodate varying levels of demand, from a few requests per hour to thousands per minute, without compromising on performance or availability.

- **Seamless Integration and Ease of Deployment:** The use of AWS services facilitates seamless integration within the pipeline, simplifying the deployment and management of the query service. API Gateway and Lambda's serverless architecture means that there is no need to provision or manage servers, allowing for automatic scaling and operational efficiency.

- **Cost-Effective and Reliable:** This setup not only offers a cost-effective solution by charging for actual usage rather than reserved capacity but also ensures reliability and low latency in query processing. The pay-as-you-go model of API Gateway and Lambda aligns with the need for maintaining operational efficiency while delivering robust performance.

In conclusion, the choice of AWS API Gateway and Lambda for the query service leverages the strengths of AWS's serverless computing and API management to provide a scalable, efficient, and cost-effective solution for querying vector embeddings stored in Pinecone. This ensures that users can retrieve timely and relevant search results, fulfilling the pipeline's requirements for performance and scalability.

## Testing and Validation
Video with the demo:

[![demo](https://img.youtube.com/vi/i_w2J8Xo2c4/0.jpg)](https://youtu.be/i_w2J8Xo2c4)

## Future Improvements and Considerations
To enhance the robustness, efficiency, and scalability of the document processing pipeline, several future improvements and considerations are proposed. These enhancements aim to address current limitations and prepare the system for evolving requirements:

- **Error Handling in Lambda Processing**: Implementing comprehensive error handling mechanisms within the Lambda functions is crucial. This includes more detailed logging of errors encountered during file processing, retry strategies for transient failures, and the use of dead-letter queues (DLQs) for messages that cannot be processed successfully. These measures will improve the system's resilience and reliability, ensuring smoother operation and easier troubleshooting.

- **Optimizing Sagemaker Costs:** While Amazon Sagemaker offers significant advantages in terms of scalability and managed services, its costs at scale can be a concern. Transitioning to a hybrid model where critical, high-demand tasks are handled by Sagemaker, and less critical or lower-demand tasks are offloaded to custom EC2 instances or containerized machine learning models, could offer a more cost-effective solution. Such an approach allows for better cost control while maintaining the benefits of managed services where they are most valuable.

- **Automating Lambda Deployment with Docker:** Leveraging AWS Lambda's support for container images, deploying Lambda functions as Docker containers can streamline the development and deployment process. By integrating this with CI/CD pipelines, such as GitHub Actions, updates to Lambda functions can be automated, ensuring faster rollouts and minimizing manual deployment efforts. This approach enhances the agility of the development process and ensures that the system can rapidly adapt to new requirements or improvements.

- **Infrastructure as Code (IaC) Adoption:** To further enhance the pipeline's scalability, reliability, and ease of management, adopting an Infrastructure as Code (IaC) approach using tools like Terraform or the Serverless Framework is highly recommended. IaC allows for the provisioning and management of cloud infrastructure through code, enabling automatic setup, scaling, and adjustment of resources according to predefined configurations. 

- **Enhanced Monitoring and Alerts:** Establishing a more comprehensive monitoring and alerting framework using AWS CloudWatch and AWS Lambda Insights will provide deeper insights into the performance and health of the system. Setting up alerts for anomalies or performance degradation will enable proactive maintenance and minimize downtime. Incorporating application performance monitoring (APM) tools can also offer more granular visibility into the execution and performance of the Lambda functions.

- **Comprehensive Testing Strategy:** Developing a robust testing strategy that includes unit tests, integration tests, and load tests is essential for ensuring the reliability and scalability of the pipeline. Automated testing as part of the CI/CD pipeline ensures that changes are validated before deployment, reducing the risk of introducing errors into the production environment.

- **Data Privacy and Security Enhancements:** As the pipeline processes potentially sensitive documents, continuously reviewing and enhancing data privacy and security measures is paramount. This could include implementing stricter access controls, encryption in transit and at rest, and regular security audits to identify and mitigate potential vulnerabilities.

By addressing these areas for improvement, the document processing pipeline can achieve higher levels of efficiency, reliability, and scalability. These enhancements will prepare the system for future growth and evolving business requirements, ensuring it remains a valuable asset in document processing and analysis tasks.
