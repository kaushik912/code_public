# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/kstreams_demo/KstreamsDemoApplication.java

```java
package com.example.kstreams_demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class KstreamsDemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(KstreamsDemoApplication.class, args);
	}

}
```

---

## File: src/main/java/com/example/kstreams_demo/WordCountTopology.java

```java
package com.example.kstreams_demo;

import java.util.Arrays;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafkaStreams;

/**
 * The whole streaming job. @EnableKafkaStreams makes Spring build a
 * StreamsBuilder, hand it to every KStream @Bean below, then start the
 * topology automatically when the app boots.
 */
@Configuration
@EnableKafkaStreams
public class WordCountTopology {

	@Bean
	public KStream<String, String> wordCountStream(StreamsBuilder builder) {
		// 1. SOURCE: read the input topic as an unbounded stream of records.
		//    key = null, value = a line of text.
		KStream<String, String> lines = builder.stream("words-input");

		lines
				// 2. STATELESS: split each line into individual words (one record -> many).
				.flatMapValues(line -> Arrays.asList(line.toLowerCase().split("\\W+")))
				.filter((key, word) -> !word.isBlank())

				// 3. RE-KEY: move the word into the KEY so records for the same word
				//    land in the same partition / same aggregation bucket.
				.groupBy((key, word) -> word)

				// 4. STATEFUL: count per key. This builds a KTable backed by a local
				//    RocksDB state store ("counts-store") + a changelog topic for fault tolerance.
				.count(Materialized.as("counts-store"))

				// 5. SINK: turn the changing table back into a stream of updates and
				//    write (word -> count) to the output topic.
				.toStream()
				.to("words-output", Produced.with(Serdes.String(), Serdes.Long()));

		return lines;
	}
}
```

---

## File: src/main/java/com/example/kstreams_demo/WordProducer.java

```java
package com.example.kstreams_demo;

import java.util.List;

import org.springframework.boot.CommandLineRunner;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

/**
 * On startup, publish a few sentences to words-input so the topology has
 * something to chew on. In real life another service would produce these.
 */
@Component
public class WordProducer implements CommandLineRunner {

	private final KafkaTemplate<String, String> template;

	public WordProducer(KafkaTemplate<String, String> template) {
		this.template = template;
	}

	@Override
	public void run(String... args) {
		List<String> sentences = List.of(
				"the quick brown fox",
				"the lazy dog",
				"the quick fox jumps over the lazy dog");

		sentences.forEach(line -> {
			template.send("words-input", line);
			System.out.println("PRODUCED >> " + line);
		});
	}
}
```

---

## File: src/main/resources/application.properties

```
spring.application.name=kstreams-demo

# --- Broker ---
spring.kafka.bootstrap-servers=localhost:9092

# --- Kafka Streams app ---
# application-id is the identity of this streams app: it names the consumer
# group AND prefixes the internal state-store / changelog topics.
spring.kafka.streams.application-id=wordcount-app
spring.kafka.streams.properties.default.key.serde=org.apache.kafka.common.serialization.Serdes$StringSerde
spring.kafka.streams.properties.default.value.serde=org.apache.kafka.common.serialization.Serdes$StringSerde
# Emit every count update immediately (great for a demo; off in prod for throughput).
spring.kafka.streams.properties.statestore.cache.max.bytes=0
spring.kafka.streams.properties.commit.interval.ms=500

# --- Plain producer (used by WordProducer to feed words-input) ---
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.apache.kafka.common.serialization.StringSerializer

# --- Plain consumer (used by CountConsumer to print words-output) ---
# words-output values are Long counts, so use the Long deserializer.
spring.kafka.consumer.group-id=demo-printer
spring.kafka.consumer.auto-offset-reset=earliest
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.apache.kafka.common.serialization.LongDeserializer
```

---

## File: src/test/java/com/example/kstreams_demo/KstreamsDemoApplicationTests.java

```java
package com.example.kstreams_demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class KstreamsDemoApplicationTests {

	@Test
	void contextLoads() {
	}

}
```

---

