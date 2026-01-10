from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class SupabaseClient:
    """Wrapper for Supabase client operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
        logger.info("Supabase client initialized")
    
    def test_connection(self) -> bool:
        """Test connection to Supabase."""
        try:
            # Simple query to test connection
            result = self.client.table("interactions").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def insert_interaction(self, interaction_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert an interaction record.
        
        Args:
            interaction_data: Dictionary with interaction fields
        
        Returns:
            Interaction ID if successful, None otherwise
        """
        try:
            result = self.client.table("interactions").insert(interaction_data).execute()
            if result.data and len(result.data) > 0:
                interaction_id = result.data[0]["id"]
                logger.info(f"Interaction logged: {interaction_id}")
                return interaction_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert interaction: {e}")
            return None
    
    def insert_escalation(self, escalation_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert an escalation record.
        
        Args:
            escalation_data: Dictionary with escalation fields
        
        Returns:
            Escalation ID if successful, None otherwise
        """
        try:
            result = self.client.table("escalations").insert(escalation_data).execute()
            if result.data and len(result.data) > 0:
                escalation_id = result.data[0]["id"]
                logger.info(f"Escalation logged: {escalation_id}")
                return escalation_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert escalation: {e}")
            return None
    
    def insert_knowledge_document(self, doc_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a knowledge document record.
        
        Args:
            doc_data: Dictionary with document fields
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            result = self.client.table("knowledge_documents").insert(doc_data).execute()
            if result.data and len(result.data) > 0:
                doc_id = result.data[0]["id"]
                logger.info(f"Knowledge document logged: {doc_id}")
                return doc_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert knowledge document: {e}")
            return None
    
    def get_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get aggregated metrics for dashboard.
        
        Args:
            filters: Optional filters (mode, date_range, etc.)
        
        Returns:
            Dictionary with metric values
        """
        try:
            # Build query with filters
            query = self.client.table("interactions").select("*")
            
            if filters:
                if "mode" in filters:
                    query = query.eq("assistant_mode", filters["mode"])
                if "date_from" in filters:
                    query = query.gte("timestamp", filters["date_from"])
                if "date_to" in filters:
                    query = query.lte("timestamp", filters["date_to"])
            
            result = query.execute()
            interactions = result.data if result.data else []
            
            # Calculate metrics (will be implemented in Task 16)
            # For now, return basic structure
            return {
                "total_interactions": len(interactions),
                "interactions": interactions
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"total_interactions": 0, "interactions": []}
    
    def get_interactions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get interactions from database with optional filters.
        
        Args:
            filters: Optional filters dict with keys:
                - mode: 'customer' or 'banker'
                - start_date: datetime or ISO string
                - end_date: datetime or ISO string
                - intent: intent name
        
        Returns:
            List of interaction dictionaries
        """
        try:
            query = self.client.table("interactions").select("*")
            
            if filters:
                if filters.get("mode"):
                    query = query.eq("assistant_mode", filters["mode"])
                if filters.get("start_date"):
                    start_date = filters["start_date"]
                    if isinstance(start_date, str):
                        query = query.gte("timestamp", start_date)
                    else:
                        query = query.gte("timestamp", start_date.isoformat())
                if filters.get("end_date"):
                    end_date = filters["end_date"]
                    if isinstance(end_date, str):
                        query = query.lte("timestamp", end_date)
                    else:
                        query = query.lte("timestamp", end_date.isoformat())
                if filters.get("intent"):
                    query = query.eq("intent_name", filters["intent"])
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get interactions: {e}")
            return []
    
    def get_escalations(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get escalations from database with optional filters.
        
        Args:
            filters: Optional filters dict with keys:
                - mode: 'customer' or 'banker' (applied after join)
                - start_date: datetime or ISO string
                - end_date: datetime or ISO string
        
        Returns:
            List of escalation dictionaries (joined with interactions for mode/intent)
        """
        try:
            # First get escalations
            query = self.client.table("escalations").select("*")
            
            if filters:
                if filters.get("start_date"):
                    start_date = filters["start_date"]
                    if isinstance(start_date, str):
                        query = query.gte("created_at", start_date)
                    else:
                        query = query.gte("created_at", start_date.isoformat())
                if filters.get("end_date"):
                    end_date = filters["end_date"]
                    if isinstance(end_date, str):
                        query = query.lte("created_at", end_date)
                    else:
                        query = query.lte("created_at", end_date.isoformat())
            
            result = query.execute()
            escalations = result.data if result.data else []
            
            # Get interaction IDs
            interaction_ids = [e.get("interaction_id") for e in escalations if e.get("interaction_id")]
            
            # Fetch interactions separately (Supabase doesn't support .in_() directly, fetch all and filter)
            interactions_map = {}
            if interaction_ids:
                # Fetch all interactions and filter in Python
                interactions_result = self.client.table("interactions").select("id, assistant_mode, intent_name").execute()
                if interactions_result.data:
                    for interaction in interactions_result.data:
                        if interaction["id"] in interaction_ids:
                            interactions_map[interaction["id"]] = interaction
            
            # Combine escalations with interaction data
            flattened = []
            for esc in escalations:
                interaction_id = esc.get("interaction_id")
                interaction = interactions_map.get(interaction_id) if interaction_id else None
                
                flattened.append({
                    "id": esc.get("id"),
                    "interaction_id": interaction_id,
                    "trigger_type": esc.get("trigger_type"),
                    "escalation_reason": esc.get("escalation_reason"),
                    "created_at": esc.get("created_at"),
                    "assistant_mode": interaction.get("assistant_mode") if interaction else None,
                    "intent_name": interaction.get("intent_name") if interaction else None,
                })
            
            # Apply mode filter if needed
            if filters and filters.get("mode"):
                flattened = [e for e in flattened if e.get("assistant_mode") == filters["mode"]]
            
            return flattened
        except Exception as e:
            logger.error(f"Failed to get escalations: {e}")
            return []
    
    def get_distinct_intents(self) -> List[str]:
        """Get list of distinct intent names from interactions."""
        try:
            result = self.client.table("interactions").select("intent_name").execute()
            intents = set()
            if result.data:
                for row in result.data:
                    intent = row.get("intent_name")
                    if intent:
                        intents.add(intent)
            return sorted(list(intents))
        except Exception as e:
            logger.error(f"Failed to get distinct intents: {e}")
            return []
    
    def get_document_metadata_by_file_ids(self, file_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get document metadata (title, source_url) for given OpenAI file IDs.

        Args:
            file_ids: List of OpenAI file IDs

        Returns:
            Dictionary mapping file_id to metadata dict with keys: title, source_url, content_type
        """
        if not file_ids:
            return {}

        try:
            # Query knowledge_documents table for matching file IDs
            # Try using .in_() first (supported in newer Supabase clients)
            try:
                result = self.client.table("knowledge_documents").select(
                    "openai_file_id, title, source_url, content_type"
                ).in_("openai_file_id", file_ids).execute()
            except (AttributeError, TypeError):
                # Fallback: fetch all and filter in Python (if .in_() not supported)
                logger.warning("in_() not supported, using fallback method")
                all_result = self.client.table("knowledge_documents").select(
                    "openai_file_id, title, source_url, content_type"
                ).execute()
                # Filter in Python
                filtered_data = []
                if all_result.data:
                    file_ids_set = set(file_ids)
                    for row in all_result.data:
                        if row.get("openai_file_id") in file_ids_set:
                            filtered_data.append(row)
                result = type('obj', (object,), {'data': filtered_data})()

            metadata_map = {}
            if result.data:
                for row in result.data:
                    file_id = row.get("openai_file_id")
                    if file_id:
                        metadata_map[file_id] = {
                            "title": row.get("title", "Unknown Document"),
                            "source_url": row.get("source_url", ""),
                            "content_type": row.get("content_type", "public")
                        }

            logger.info(
                "document_metadata_retrieved",
                requested_count=len(file_ids),
                found_count=len(metadata_map)
            )
            return metadata_map
        except Exception as e:
            logger.error(f"Failed to get document metadata: {e}")
            return {}

    def get_intent_risk_value_matrix(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get intent risk-value matrix data for dashboard.

        For each intent, calculates:
        - Containment rate (value): % of interactions that were resolved
        - Escalation rate (risk): % of interactions that were escalated
        - Volume: total number of interactions

        Args:
            filters: Optional filters dict

        Returns:
            List of dicts with keys: intent_name, containment_rate, escalation_rate, volume
        """
        try:
            # Get interactions data
            interactions = self.get_interactions(filters)

            if not interactions:
                return []

            # Group by intent
            intent_stats = {}
            for interaction in interactions:
                intent = interaction.get("intent_name")
                if not intent:
                    continue

                outcome = interaction.get("outcome")
                if intent not in intent_stats:
                    intent_stats[intent] = {"total": 0, "resolved": 0, "escalated": 0}

                intent_stats[intent]["total"] += 1
                if outcome == "resolved":
                    intent_stats[intent]["resolved"] += 1
                elif outcome == "escalated":
                    intent_stats[intent]["escalated"] += 1

            # Calculate rates
            matrix_data = []
            for intent, stats in intent_stats.items():
                total = stats["total"]
                if total == 0:
                    continue

                containment_rate = (stats["resolved"] / total) * 100
                escalation_rate = (stats["escalated"] / total) * 100

                matrix_data.append({
                    "intent_name": intent,
                    "containment_rate": containment_rate,
                    "escalation_rate": escalation_rate,
                    "volume": total
                })

            # Sort by volume descending
            matrix_data.sort(key=lambda x: x["volume"], reverse=True)

            logger.info(f"Intent risk-value matrix calculated for {len(matrix_data)} intents")
            return matrix_data

        except Exception as e:
            logger.error(f"Failed to calculate intent risk-value matrix: {e}")
            return []

    def get_citation_coverage_data(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get citation coverage and source health data for dashboard.

        Calculates:
        - Citation coverage rate: % of responses with citations
        - Top source pages: most frequently cited sources
        - Failed retrieval rate: % of responses with 0 retrieved chunks

        Args:
            filters: Optional filters dict

        Returns:
            Dict with keys: citation_coverage_rate, failed_retrieval_rate, top_sources
        """
        try:
            # Get interactions data
            interactions = self.get_interactions(filters)

            if not interactions:
                return {
                    "citation_coverage_rate": 0.0,
                    "failed_retrieval_rate": 0.0,
                    "top_sources": []
                }

            total_responses = 0
            responses_with_citations = 0
            failed_retrievals = 0
            source_counts = {}

            for interaction in interactions:
                # Only count interactions that generated responses
                if interaction.get("response_text"):
                    total_responses += 1

                    # Check citations
                    citations = interaction.get("citations", [])
                    if citations and len(citations) > 0:
                        responses_with_citations += 1

                        # Count sources
                        for citation in citations:
                            source = citation.get("source", "")
                            if source:
                                source_counts[source] = source_counts.get(source, 0) + 1

                    # Check retrieval success
                    retrieved_chunks = interaction.get("retrieved_chunks_count", 0)
                    if retrieved_chunks == 0:
                        failed_retrievals += 1

            # Calculate rates
            citation_coverage_rate = (responses_with_citations / total_responses * 100) if total_responses > 0 else 0.0
            failed_retrieval_rate = (failed_retrievals / total_responses * 100) if total_responses > 0 else 0.0

            # Get top sources
            top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_sources = [{"source": source, "count": count} for source, count in top_sources]

            result = {
                "citation_coverage_rate": citation_coverage_rate,
                "failed_retrieval_rate": failed_retrieval_rate,
                "top_sources": top_sources,
                "total_responses": total_responses
            }

            logger.info(f"Citation coverage data calculated: {citation_coverage_rate:.1f}% coverage, {failed_retrieval_rate:.1f}% failed retrieval, {len(top_sources)} top sources")
            return result

        except Exception as e:
            logger.error(f"Failed to calculate citation coverage data: {e}")
            return {
                "citation_coverage_rate": 0.0,
                "failed_retrieval_rate": 0.0,
                "top_sources": []
            }

    def create_conversation(self, conversation_id: str, assistant_mode: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new conversation.

        Args:
            conversation_id: Unique conversation identifier
            assistant_mode: 'customer' or 'banker'
            user_id: Optional user identifier

        Returns:
            Conversation UUID if successful, None otherwise
        """
        try:
            data = {
                "conversation_id": conversation_id,
                "assistant_mode": assistant_mode,
                "user_id": user_id,
                "is_active": True
            }
            result = self.client.table("conversations").insert(data).execute()
            if result.data and len(result.data) > 0:
                conversation_uuid = result.data[0]["id"]
                logger.info(f"Conversation created: {conversation_id} (UUID: {conversation_uuid})")
                return conversation_uuid
            return None
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation metadata by conversation_id.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation dict if found, None otherwise
        """
        try:
            result = self.client.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    def save_message(self, conversation_uuid: str, role: str, content: str,
                    citations: Optional[List[Dict[str, Any]]] = None,
                    confidence_score: Optional[float] = None,
                    escalated: bool = False,
                    escalation_message: Optional[str] = None,
                    trigger_type: Optional[str] = None,
                    interaction_id: Optional[str] = None) -> Optional[str]:
        """
        Save a message to a conversation.

        Args:
            conversation_uuid: Conversation UUID
            role: 'user', 'assistant', or 'system'
            content: Message content
            citations: Optional citations for assistant messages
            confidence_score: Optional confidence score for assistant messages
            escalated: Whether this message represents an escalation
            escalation_message: Escalation message if escalated
            trigger_type: Escalation trigger type
            interaction_id: Link to detailed interaction log

        Returns:
            Message UUID if successful, None otherwise
        """
        try:
            data = {
                "conversation_id": conversation_uuid,
                "role": role,
                "content": content,
                "citations": citations,
                "confidence_score": confidence_score,
                "escalated": escalated,
                "escalation_message": escalation_message,
                "trigger_type": trigger_type,
                "interaction_id": interaction_id
            }
            result = self.client.table("conversation_messages").insert(data).execute()
            if result.data and len(result.data) > 0:
                message_uuid = result.data[0]["id"]
                logger.debug(f"Message saved to conversation {conversation_uuid}: {role}")
                return message_uuid

            # Update conversation's message count and updated_at
            self.client.table("conversations").update({
                "message_count": self.client.table("conversations").select("message_count").eq("id", conversation_uuid).execute().data[0]["message_count"] + 1,
                "updated_at": "now()"
            }).eq("id", conversation_uuid).execute()

            return None
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return None

    def load_conversation_history(self, conversation_uuid: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load conversation history (messages) for a conversation.

        Args:
            conversation_uuid: Conversation UUID
            limit: Optional limit on number of messages (most recent first)

        Returns:
            List of message dictionaries ordered by timestamp
        """
        try:
            query = self.client.table("conversation_messages").select("*").eq("conversation_id", conversation_uuid).order("timestamp", desc=False)
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to load conversation history: {e}")
            return []

    def get_recent_conversations(self, user_id: Optional[str] = None, assistant_mode: Optional[str] = None,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations for a user or all active conversations.

        Args:
            user_id: Optional user identifier to filter by
            assistant_mode: Optional assistant mode to filter by
            limit: Maximum number of conversations to return

        Returns:
            List of conversation dictionaries ordered by updated_at desc
        """
        try:
            query = self.client.table("conversations").select("*").eq("is_active", True).order("updated_at", desc=True).limit(limit)

            if user_id:
                query = query.eq("user_id", user_id)
            if assistant_mode:
                query = query.eq("assistant_mode", assistant_mode)

            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []

    def update_conversation_title(self, conversation_uuid: str, title: str) -> bool:
        """
        Update conversation title (auto-generated from first user message).

        Args:
            conversation_uuid: Conversation UUID
            title: New title

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.table("conversations").update({
                "title": title,
                "updated_at": "now()"
            }).eq("id", conversation_uuid).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update conversation title: {e}")
            return False

# Singleton instance
_db_client: Optional[SupabaseClient] = None

def get_db_client() -> SupabaseClient:
    """Get singleton Supabase client instance."""
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client
