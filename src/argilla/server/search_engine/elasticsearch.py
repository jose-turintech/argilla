#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import dataclasses
from typing import Any, Dict, List, Optional

from elasticsearch8 import AsyncElasticsearch, helpers

from argilla.server.search_engine import (
    SearchEngine,
)
from argilla.server.search_engine.commons import BaseElasticAndOpenSearchEngine
from argilla.server.settings import settings


def _compute_num_candidates_from_k(k: int) -> int:
    if k < 50:
        return 500
    elif 50 <= k < 200:
        return 100
    return 2000


@SearchEngine.register(engine_name="elasticsearch")
@dataclasses.dataclass
class ElasticSearchEngine(BaseElasticAndOpenSearchEngine):
    config: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.client = AsyncElasticsearch(**self.config)

    @classmethod
    async def new_instance(cls) -> "ElasticSearchEngine":
        config = dict(
            hosts=settings.elasticsearch,
            verify_certs=settings.elasticsearch_ssl_verify,
            ca_certs=settings.elasticsearch_ca_path,
            retry_on_timeout=True,
            max_retries=5,
        )
        return cls(
            config=config,
            number_of_shards=settings.es_records_index_shards,
            number_of_replicas=settings.es_records_index_replicas,
        )

    async def close(self):
        await self.client.close()

    def _configure_index_settings(self) -> Dict[str, Any]:
        return {
            "max_result_window": self.max_result_window,
            "number_of_shards": self.number_of_shards,
            "number_of_replicas": self.number_of_replicas,
        }

    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        await self.client.indices.create(index=index_name, settings=settings, mappings=mappings)

    async def _delete_index_request(self, index_name: str):
        await self.client.indices.delete(index_name, ignore=[404], ignore_unavailable=True)

    async def _update_document_request(self, index_name: str, id: str, body: dict):
        await self.client.update(index=index_name, id=id, **body)

    async def put_index_mapping_request(self, index: str, mappings: dict):
        await self.client.indices.put_mapping(index=index, properties=mappings)

    async def _index_search_request(
        self,
        index: str,
        query: dict,
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: str = None,
        aggregations: Optional[dict] = None,
    ) -> dict:
        return await self.client.search(
            index=index,
            query=query,
            from_=from_,
            size=size,
            source=False,
            aggregations=aggregations,
            sort=sort or "_score:desc,id:asc",
            track_total_hits=True,
        )

    async def _index_exists_request(self, index_name: str) -> bool:
        return await self.client.indices.exists(index=index_name)

    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        _, errors = await helpers.async_bulk(client=self.client, actions=actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)

    async def _refresh_index_request(self, index_name: str):
        await self.client.indices.refresh(index_name)
