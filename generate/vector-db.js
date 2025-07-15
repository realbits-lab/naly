import fs from 'fs';
import { OpenAIEmbeddings } from '@langchain/openai';

class VectorDatabase {
  constructor(dbPath = './vector-db.json') {
    this.dbPath = dbPath;
    this.embeddings = new OpenAIEmbeddings({
      model: "text-embedding-3-small",
    });
    this.documents = [];
    this.vectors = [];
    this.loadDatabase();
  }

  loadDatabase() {
    try {
      if (fs.existsSync(this.dbPath)) {
        const data = JSON.parse(fs.readFileSync(this.dbPath, 'utf-8'));
        this.documents = data.documents || [];
        this.vectors = data.vectors || [];
        console.log(`Loaded ${this.documents.length} documents from database`);
      }
    } catch (error) {
      console.error('Error loading database:', error);
      this.documents = [];
      this.vectors = [];
    }
  }

  saveDatabase() {
    try {
      const data = {
        documents: this.documents,
        vectors: this.vectors,
        lastUpdated: new Date().toISOString()
      };
      fs.writeFileSync(this.dbPath, JSON.stringify(data, null, 2));
      console.log(`Saved ${this.documents.length} documents to database`);
    } catch (error) {
      console.error('Error saving database:', error);
    }
  }

  async addDocuments(chunks) {
    console.log(`Adding ${chunks.length} chunks to vector database...`);
    
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      
      try {
        // Generate embedding for the chunk
        const embedding = await this.embeddings.embedQuery(chunk.text);
        
        // Store document and vector
        this.documents.push({
          id: chunk.id,
          text: chunk.text,
          metadata: chunk.metadata,
          addedAt: new Date().toISOString()
        });
        
        this.vectors.push({
          id: chunk.id,
          embedding: embedding
        });
        
        console.log(`Processed chunk ${i + 1}/${chunks.length}: ${chunk.id}`);
      } catch (error) {
        console.error(`Error processing chunk ${chunk.id}:`, error);
      }
    }
    
    this.saveDatabase();
    console.log('All chunks added to vector database');
  }

  async search(query, topK = 5) {
    if (this.documents.length === 0) {
      return [];
    }

    try {
      // Generate embedding for the query
      const queryEmbedding = await this.embeddings.embedQuery(query);
      
      // Calculate similarities
      const similarities = this.vectors.map((vector, index) => ({
        index,
        similarity: this.cosineSimilarity(queryEmbedding, vector.embedding),
        document: this.documents[index]
      }));
      
      // Sort by similarity and return top results
      similarities.sort((a, b) => b.similarity - a.similarity);
      
      return similarities.slice(0, topK).map(item => ({
        document: item.document,
        similarity: item.similarity
      }));
    } catch (error) {
      console.error('Error searching database:', error);
      return [];
    }
  }

  cosineSimilarity(a, b) {
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    return dotProduct / (magnitudeA * magnitudeB);
  }

  getStats() {
    const stats = {
      totalDocuments: this.documents.length,
      totalVectors: this.vectors.length,
      documentTypes: {},
      hierarchyLevels: {},
      sections: {}
    };

    this.documents.forEach(doc => {
      // Count document types
      const type = doc.metadata.type;
      stats.documentTypes[type] = (stats.documentTypes[type] || 0) + 1;
      
      // Count hierarchy levels
      const level = doc.metadata.level;
      stats.hierarchyLevels[level] = (stats.hierarchyLevels[level] || 0) + 1;
      
      // Count sections
      const section = doc.metadata.section;
      if (section) {
        stats.sections[section] = (stats.sections[section] || 0) + 1;
      }
    });

    return stats;
  }

  findByMetadata(filters) {
    return this.documents.filter(doc => {
      return Object.entries(filters).every(([key, value]) => {
        if (key === 'hierarchy') {
          return doc.metadata.hierarchy?.includes(value);
        }
        return doc.metadata[key] === value;
      });
    });
  }

  clear() {
    this.documents = [];
    this.vectors = [];
    this.saveDatabase();
  }
}

export default VectorDatabase;